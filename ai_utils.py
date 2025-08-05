import os
import json
import time
import pandas as pd
import numpy as np
from io import StringIO
from sqlalchemy import text
from threading import Lock
from dotenv import load_dotenv
from sql_agent import get_sql_agent
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime
from database import execute_query
from typing import Dict, Any, Optional, List
import re
import logging
from functools import lru_cache
import gc

load_dotenv()

bedrock_call_lock = Lock()
last_bedrock_call_time = 0
MIN_CALL_INTERVAL = 1.0

# Lazy loading for memory-heavy components
_sentence_model = None
_generic_embeddings = None

def get_sentence_model():
    """Lazy load the sentence transformer model - using lightweight model"""
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer
        # Using much lighter model to save memory and improve performance
        _sentence_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    return _sentence_model

def get_generic_embeddings():
    """Lazy load generic response embeddings - focused on DB-related generic responses"""
    global _generic_embeddings
    if _generic_embeddings is None:
        from sentence_transformers import util
        # More specific generic responses that indicate database query is needed
        GENERIC_RESPONSES = [
            "I don't have that information about your data.",
            "I don't have access to your database.",
            "I cannot provide information about your farm data.",
            "I don't know about your specific data.",
            "I don't have information about your farm.",
            "I cannot access your farm records."
        ]
        model = get_sentence_model()
        _generic_embeddings = model.encode(GENERIC_RESPONSES)
    return _generic_embeddings

def call_bedrock(prompt: str, system_prompt: str = "") -> str:
    global last_bedrock_call_time
    with bedrock_call_lock:
        current_time = time.time()
        elapsed = current_time - last_bedrock_call_time
        if elapsed < MIN_CALL_INTERVAL:
            time.sleep(MIN_CALL_INTERVAL - elapsed)
        try:
            import boto3
            bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv("AWS_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,
                "system": system_prompt,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            })
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                contentType='application/json',
                accept='application/json',
                body=body
            )
            last_bedrock_call_time = time.time()
            result = json.loads(response['body'].read())
            text = result['content'][0]['text']
            if "anthropic" in text.lower():
                return "Hi, I am Ketha AI! Ask me anything about your farm data."
            return text
        except Exception as e:
            print("Bedrock Error:", str(e))
            return f"An error occurred: {str(e)}"

@lru_cache(maxsize=1)
def get_schema_words():
    from sql_agent import get_schema_summary
    schema = get_schema_summary()
    schema_words = set()
    for line in schema.splitlines():
        parts = re.split(r'[\s\-,()]+', line)
        schema_words.update([w.lower() for w in parts if w and w.isalpha()])
    return schema_words

def needs_db_query(query: str) -> bool:
    """Determine if a query needs database access"""
    query_lower = query.lower().strip()
    
    # Simple greetings that definitely don't need DB
    simple_greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "greetings", "hola", "bonjour"
    ]
    
    # Check for exact matches or very short greetings
    if query_lower in simple_greetings or len(query_lower) <= 3:
        logging.info("Routing to Bedrock: simple greeting")
        return False
    
    # General non-data questions that should go to Bedrock
    general_patterns = [
        r"what.*(weather|time|day|today)",
        r"how to (cook|make|do|learn)",
        r"what is (the|a) (capital|currency|population)",
        r"who is the (president|minister|king|queen|leader)",
        r"tell me about (history|science|politics)",
        r"explain (physics|chemistry|biology)",
        r"what does .* mean"
    ]
    
    for pattern in general_patterns:
        if re.search(pattern, query_lower):
            logging.info(f"Routing to Bedrock: matched general pattern '{pattern}'")
            return False
    
    # Contextual follow-up questions that likely refer to farm data
    # These are very specific patterns for short follow-up questions
    contextual_patterns = [
        r"^who was (it|that|this)\s*from\s*\??$",
        r"^who (did|made|performed) (it|that|this)\s*\??$",
        r"^when was (it|that|this)\s*\??$",
        r"^how much was (it|that|this)\s*\??$",
        r"^what about (it|that|this)\s*\??$",
        r"^(and )?who collected\s*\??$",
        r"^(and )?who paid\s*\??$",
        r"^which (farmer|chiller|staff)\s*\??$",
        r"^who brought (it|that|this)\s*\??$",
        r"^who delivered (it|that|this)\s*\??$"
    ]
    
    for pattern in contextual_patterns:
        if re.search(pattern, query_lower):
            logging.info(f"Routing to DB: matched contextual pattern '{pattern}'")
            return True
    
    # Database-related keywords
    keywords = [
        "data", "milk", "collection", "farmer", "payment", "report", "table", 
        "list", "show", "how many", "total", "average", "sum", "trend", 
        "analysis", "analyze", "visualize", "graph", "chart", "statistics",
        "name", "info", "information", "details", "describe", "which", "who", "when", "where", "my", "id",
        "count", "amount", "number", "history", "record", "records", "summary", "status", "balance", "due",
        "chiller", "farmer", "staff", "user", "zone", "transporter", "payment", "collection", "date", "quantity"
    ]
    
    schema_words = get_schema_words()
    keywords.extend(schema_words)
    
    # More specific patterns for data-related "what" questions
    data_what_patterns = [
        r"what is my (chiller|farmer|staff|user)",
        r"what are my (farmers|collections|payments)",
        r"what is the (total|amount|quantity|balance)",
        r"what.*my (data|farm|business)"
    ]
    
    # Check for data-specific "what" questions first
    for pattern in data_what_patterns:
        if re.search(pattern, query_lower):
            logging.info(f"Routing to DB: matched data 'what' pattern '{pattern}'")
            return True
    
    entity_patterns = [
        r"\bmy\b", r"\bour\b", r"\bthe\b", r"\bthis\b", r"\bthese\b",
        r"\bchiller\s+\d+\b", r"\bfarm(er)?\s+\d+\b", r"\bstaff\s+\d+\b", r"\buser\s+\d+\b",
        r"\bid\s*=\s*\d+\b", r"\bchiller\s+name\b", r"\bfarm(er)?\s+name\b"
    ]
    
    for keyword in keywords:
        # Skip generic words that might appear in non-data contexts
        if keyword in ["what", "when", "where", "who", "which"]:
            continue
        if re.search(rf"\b{re.escape(keyword)}\b", query_lower):
            logging.info(f"Routing to DB: matched keyword '{keyword}'")
            return True
            
    for pattern in entity_patterns:
        if re.search(pattern, query_lower):
            logging.info(f"Routing to DB: matched pattern '{pattern}'")
            return True
            
    if re.search(r"\b\d+\b", query_lower) and any(entity in query_lower for entity in ["chiller", "farmer", "staff", "user"]):
        logging.info("Routing to DB: contains number and known entity")
        return True
        
    # Only check for question words with farm-specific context
    question_words = ["what", "who", "when", "where", "how", "which"]
    if any(query_lower.startswith(qw) for qw in question_words):
        if any(entity in query_lower for entity in ["chiller", "farmer", "milk", "collection", "payment", "farm", "data"]):
            logging.info("Routing to DB: question word with farm context")
            return True
            
    logging.info("Routing to Bedrock: no DB match")
    return False

def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"insights": "No data available for analysis"}
    
    analysis = {"insights": f"Found {len(df)} records"}
    numeric_cols = df.select_dtypes(include=np.number).columns
    
    if len(numeric_cols) > 0:
        main_col = numeric_cols[0]
        # Use more memory-efficient operations
        col_data = df[main_col].dropna()
        if not col_data.empty:
            analysis.update({
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "max": float(col_data.max()),
                "min": float(col_data.min()),
                "insights": f"Data ranges from {col_data.min()} to {col_data.max()}"
            })
    return analysis

def format_results(data) -> Dict[str, Any]:
    if not data:
        return {
            "markdown": "No data available",
            "json": {"data": []},
            "csv": ""
        }
    try:
        # Limit data size to prevent memory issues
        limited_data = data[:1000] if len(data) > 1000 else data
        df = pd.DataFrame(limited_data)
        
        # Use more memory-efficient operations
        markdown = df.to_markdown(index=False, max_rows=50)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv = csv_buffer.getvalue()
        csv_buffer.close()  # Explicitly close to free memory
        
        return {
            "markdown": markdown,
            "json": {"data": limited_data},
            "csv": csv
        }
    except Exception as e:
        print(f"Formatting error: {str(e)}")
        return {
            "markdown": "Error formatting results",
            "json": {"error": str(e)},
            "csv": ""
        }

def generate_chart_config(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    if df.empty:
        return None
        
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)
    quantity_col = next((col for col in df.columns if 'quantity' in col.lower() or 'total' in col.lower()), None)
    
    if not date_col or not quantity_col:
        return None
        
    try:
        # Limit chart data to prevent memory issues
        chart_data = df.head(100) if len(df) > 100 else df
        labels = chart_data[date_col].astype(str).tolist()
        data_values = chart_data[quantity_col].astype(float).tolist()
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": quantity_col,
                    "data": data_values,
                    "backgroundColor": "rgba(255, 140, 0, 0.5)",
                    "borderColor": "rgba(255, 140, 0, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {"y": {"beginAtZero": True}}
            }
        }
    except Exception as e:
        print(f"Chart generation error: {str(e)}")
        return None

def is_generic_response(text: str, threshold: float = 0.85) -> bool:
    """Check if response is generic - only flag true generics that indicate DB query needed"""
    if not text or len(text.strip()) == 0:
        return True
    
    text_lower = text.lower().strip()
    
    # Don't flag short responses like greetings as generic
    if len(text_lower.split()) < 6:
        # Check if it's a greeting or similar non-generic short response
        greeting_patterns = [
            r"^(hi|hello|hey|good morning|good afternoon|good evening)",
            r"how are you",
            r"nice to meet",
            r"thank you",
            r"thanks",
            r"you're welcome",
            r"goodbye|bye"
        ]
        if any(re.search(pattern, text_lower) for pattern in greeting_patterns):
            return False  # Greetings are not generic
    
    # Only flag responses that explicitly indicate lack of information about data
    TRULY_GENERIC_RESPONSES = [
        "i don't have that information",
        "i don't have information about",
        "i don't have access to",
        "i cannot access",
        "i don't know about your",
        "i don't have data about",
        "i cannot provide information about your",
        "i don't have access to your database",
        "i cannot access your data"
    ]
    
    # Check for explicit data-related generic responses
    if any(generic in text_lower for generic in TRULY_GENERIC_RESPONSES):
        return True
    
    # More specific patterns for database-related generic responses
    DB_GENERIC_PATTERNS = [
        r"\bi (do not|don't) have (information|data) about your",
        r"\bi cannot (provide|access) (your|the) (data|information)",
        r"\bi (do not|don't) have access to your (database|data)",
        r"\bno (information|data) available about your"
    ]
    
    if any(re.search(pattern, text_lower) for pattern in DB_GENERIC_PATTERNS):
        return True
    
    # Only use semantic similarity for responses that might be data-related generics
    if any(word in text_lower for word in ["data", "information", "database", "farm", "don't", "cannot", "unable"]):
        try:
            from sentence_transformers import util
            model = get_sentence_model()
            embeddings = get_generic_embeddings()
            text_embedding = model.encode([text])
            similarities = util.cos_sim(text_embedding, embeddings)
            if similarities.max() > threshold:
                return True
        except Exception as e:
            logging.warning(f"Semantic similarity check failed: {e}")
    
    return False

def build_prompt(query: str, history: Optional[List[dict]]) -> str:
    prompt = ""
    if history:
        prompt += "Previous conversation:\n"
        for turn in history:
            if turn.get("isUser", True):
                prompt += f"User: {turn['text']}\n"
            else:
                prompt += f"AI: {turn['text']}\n"
        prompt += "\n"
    prompt += f"Current question: {query}\n"
    return prompt

def handle_db_query(query: str, chiller_id: Optional[int] = None, history: Optional[list] = None) -> Dict[str, Any]:
    if chiller_id is not None:
        prompt = f"{build_prompt(query, history or [])}\nChiller ID: {chiller_id}\n"
    else:
        prompt = build_prompt(query, history or [])
    
    agent = get_sql_agent()
    try:
        result = agent.invoke({"input": prompt})
        # Handle different possible result formats
        text = result.get("output") or result.get("final_answer") or result.get("text") or ""
        
        # Clean up the text if it contains system messages
        if "anthropic" in text.lower():
            text = "Hi, I am Ketha AI! Ask me anything about your farm data."
        
        data = result.get("data", [])
        formats = format_results(data)
        is_table = bool(data)
        is_chart = False
        chart_config = {}
        analysis = {}
        
        if data:
            df = pd.DataFrame(data)
            chart = generate_chart_config(df)
            if chart:
                is_chart = True
                chart_config = chart
            analysis = analyze_data(df)
            # Clean up DataFrame to free memory
            del df
            gc.collect()
        
        return {
            "text": text,
            "final_answer": text,
            "data": data,
            "formats": formats,
            "isReport": is_table,
            "isTable": is_table,
            "isChart": is_chart,
            "chartConfig": chart_config,
            "analysis": analysis
        }
    except Exception as e:
        logging.error(f"DB Query Error: {str(e)}", exc_info=True)
        
        # Special handling for parsing errors - try to extract useful info
        error_msg = str(e)
        if "Could not parse LLM output" in error_msg and "The last collection" in error_msg:
            # Extract the actual response from parsing error
            try:
                start = error_msg.find("The last collection")
                end = error_msg.find("For troubleshooting")
                if start != -1 and end != -1:
                    extracted_text = error_msg[start:end].strip().rstrip('`')
                    return {
                        "text": extracted_text,
                        "final_answer": extracted_text,
                        "data": [],
                        "formats": format_results([]),
                        "isReport": False,
                        "isTable": False,
                        "isChart": False,
                        "chartConfig": {},
                        "analysis": {}
                    }
            except:
                pass
        
        return {
            "text": "Sorry, I couldn't retrieve the requested data due to an internal error.",
            "final_answer": "Sorry, I couldn't retrieve the requested data due to an internal error.",
            "data": [],
            "formats": format_results([]),
            "isReport": False,
            "isTable": False,
            "isChart": False,
            "chartConfig": {},
            "analysis": {}
        }

def handle_general_query(query: str, history: Optional[list] = None) -> str:
    prompt = build_prompt(query, history or [])
    text = call_bedrock(prompt)
    if "anthropic" in text.lower():
        return "Hi, I am Ketha AI! Ask me anything about your farm data."
    return text