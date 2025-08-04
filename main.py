from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from ai_utils import handle_db_query, handle_general_query, needs_db_query
from models import AIRequest, AIResponse
import traceback
import logging
import re
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any

app = FastAPI()

# CORS configuration
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_store = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Load the model once at startup
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

GENERIC_RESPONSES = [
    "I'm not sure.",
    "I do not know.",
    "I don't have that information.",
    "Sorry, I cannot answer that.",
    "No information available.",
    "Not available.",
    "I have no idea.",
    "I am unable to answer that.",
    "I don't know the answer to that question."
]

GENERIC_PATTERNS = [
    r"\bi (do not|don't) (know|have)\b",
    r"\bno (information|data)\b",
    r"\bnot (available|sure)\b",
    r"\bsorry\b",
    r"\bcannot answer\b",
    r"\bunable to\b",
    r"\bno idea\b"
]

# Precompute embeddings for generic responses
generic_embeddings = sentence_model.encode(GENERIC_RESPONSES)

def is_generic_response(text: str, threshold: float = 0.78) -> bool:
    if not text or len(text.strip().split()) < 6:
        return True
    text_lower = text.lower()
    # Hardcoded phrases
    if any(generic.lower() in text_lower for generic in GENERIC_RESPONSES):
        return True
    # Regex patterns
    if any(re.search(pattern, text_lower) for pattern in GENERIC_PATTERNS):
        return True
    # Semantic similarity
    text_embedding = sentence_model.encode([text])
    similarities = util.cos_sim(text_embedding, generic_embeddings)
    if similarities.max() > threshold:
        return True
    # Too short or mostly hedging/modal
    hedges = ["maybe", "perhaps", "possibly", "could", "might", "unsure", "uncertain"]
    hedge_count = sum(1 for h in hedges if h in text_lower)
    if hedge_count > 0 and len(text_lower.split()) < 12:
        return True
    return False

@app.post("/query", response_model=AIResponse)
async def query_ai(request: AIRequest):
    logging.info(f"Received request: user_id={request.user_id}, query={request.query}, chiller_id={request.chiller_id}")
    user_session = session_store.setdefault(request.user_id, [])
    try:
        # Use history from request if provided, else fallback to session
        history = request.history if request.history else user_session[-4:] if len(user_session) > 0 else []
        if needs_db_query(request.query):
            response = handle_db_query(request.query, chiller_id=request.chiller_id, history=history)
            logging.info(f"AI DB Response: {response}")
            user_session.append({"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
            return {
                "text": response.get("final_answer") or response.get("text") or "Here are your results:",
                "isReport": response.get("isReport", True),
                "isTable": response.get("isTable", True),
                **response
            }
        else:
            ai_text = handle_general_query(request.query, history=history)
            logging.info(f"AI General Response: {ai_text}")
            if is_generic_response(ai_text):
                logging.info("General response was generic, falling back to DB.")
                response = handle_db_query(request.query, chiller_id=request.chiller_id, history=history)
                user_session.append({"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
                return {
                    "text": response.get("final_answer") or response.get("text") or "Here are your results:",
                    "isReport": response.get("isReport", True),
                    "isTable": response.get("isTable", True),
                    **response
                }
            user_session.append({"user": request.query, "ai": ai_text})
            return {
                "text": ai_text,
                "isReport": False
            }
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Error processing query: {error_trace}")
        return {
            "text": f"Error processing your query: {str(e)}",
            "isReport": False
        }

@app.post("/clear_conversation")
async def clear_conversation(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    chiller_id = payload.get("chiller_id")  # Not strictly needed for session, but included for completeness
    if user_id in session_store:
        session_store[user_id] = []
    logging.info(f"Cleared conversation for user_id={user_id}, chiller_id={chiller_id}")
    return {"status": "cleared"}

@app.post("/debug_route")
async def debug_route(payload: dict = Body(...)):
    query = payload.get("query", "")
    route = "db" if needs_db_query(query) else "bedrock"
    return {"route": route}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)