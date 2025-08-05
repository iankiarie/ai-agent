from langchain_community.utilities import SQLDatabase
from langchain_aws import ChatBedrock
from database import get_db_engine
from langchain.chains import create_sql_query_chain
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from sqlalchemy import inspect
from datetime import datetime
from functools import lru_cache
import logging

def validate_table_and_columns(table_name, column_names):
    """Validate that table and columns exist in the database"""
    engine = get_db_engine()
    inspector = inspect(engine)
    
    # Check if table exists
    available_tables = inspector.get_table_names()
    if table_name not in available_tables:
        return False
    
    # Check if columns exist
    try:
        table_columns = inspector.get_columns(table_name)
        available_columns = [col['name'] for col in table_columns]
        
        for col in column_names:
            if col not in available_columns:
                return False
        
        return True
    except Exception as e:
        logging.error(f"Error validating columns for table {table_name}: {e}")
        return False
import re

def get_sql_agent():
    engine = get_db_engine()
    db = SQLDatabase(engine)
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"temperature": 0.1}
    )

    schema = get_schema_summary()
    joins = get_join_guides()
    valid_schema = get_valid_tables_and_columns()
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create validation text for the prompt
    validation_text = "VALID TABLES AND COLUMNS (YOU MUST ONLY USE THESE):\n"
    for table, columns in valid_schema.items():
        validation_text += f"Table '{table}': {', '.join(columns)}\n"
    
    prompt_template = f"""
You are an expert SQL developer assistant for a farming system.

{validation_text}

Database schema with types:
{schema}

Join relationships:
{joins}

CRITICAL VALIDATION RULES - FOLLOW THESE EXACTLY:
1. ONLY use table names and column names that exist in the VALID TABLES AND COLUMNS list above.
2. If you reference a table or column that doesn't exist in the valid list, the query will FAIL.
3. Double-check every table name and column name against the valid list before generating SQL.
4. Always use table aliases for clarity.
5. Never use SELECT * - always specify exact column names from the valid list.
6. Use EXTRACT(YEAR FROM date_column) for years.
7. Use DATE_TRUNC('month', date_column) for months.
8. Handle NULL values with COALESCE.
9. For dates, use ISO format: 'YYYY-MM-DD'.
10. If the user specifies a chiller ID, always filter results by that chiller ID.
11. When referring to a chiller, always use its name from users_chiller.name (not ID), unless user explicitly asks for ID.
12. When referring to a farmer, always use their name from users_user.first_name or username (not ID), unless user explicitly asks for ID.
13. For simple greetings like "Hi", "Hello", "Hey" - respond directly without SQL queries.

BEFORE GENERATING ANY SQL:
- Verify each table name exists in the valid tables list
- Verify each column name exists for that specific table
- If a table or column doesn't exist, explain what valid options are available

Current Date: {current_date}

You have access to the following tool:
{{tools}}

Use the following format EXACTLY:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, must be: query_sql_db OR skip_sql (for greetings/non-data questions)
Action Input: the SQL query string ONLY (without any extra formatting) OR "direct_response"
Observation: the result of the action
... (this Thought/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

CRITICAL FORMAT RULES:
- For simple greetings (Hi, Hello, Hey), use: Action: skip_sql, Action Input: direct_response
- For data questions, use: Action: query_sql_db, Action Input: SQL query string only
- Action Input must contain ONLY the SQL query string (no quotes, no formatting)
- ALWAYS validate table and column names before generating SQL
- ALWAYS end with "Final Answer:" followed by your response
- If a requested table/column doesn't exist, explain available options instead of generating invalid SQL

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}
"""

    def validate_and_execute_sql(query: str):
        """Validate SQL query against schema before execution"""
        try:
            # Basic validation - check if query contains valid table names
            query_upper = query.upper()
            valid_tables = set(valid_schema.keys())
            
            # Extract potential table names from query (simple approach)
            potential_tables = []
            for table in valid_tables:
                if table.upper() in query_upper:
                    potential_tables.append(table)
            
            if not potential_tables:
                return "Error: No valid table names found in query. Available tables: " + ", ".join(valid_tables)
            
            # Execute the validated query
            return db.run(query)
        except Exception as e:
            return f"SQL execution error: {str(e)}"

    query_tool = Tool.from_function(
        name="query_sql_db",
        description="Execute SQL queries against the database with validation",
        func=validate_and_execute_sql,
    )
    
    skip_tool = Tool.from_function(
        name="skip_sql", 
        description="Skip SQL for greetings and non-data questions",
        func=lambda x: "Ready for direct response",
    )
    
    tools = [query_tool, skip_tool]
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={
            "tool_names": ", ".join([t.name for t in tools]),
            "tools": "\n".join([f"{t.name}: {t.description}" for t in tools])
        }
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=2,
        return_intermediate_steps=False
    )

@lru_cache(maxsize=1)
def get_schema_summary():
    """
    Returns a detailed schema summary with all valid table and column names.
    This will be used to validate SQL queries.
    """
    engine = get_db_engine()
    inspector = inspect(engine)
    lines = []
    
    # Get table names and their complete column information
    table_names = sorted(inspector.get_table_names())
    
    for table_name in table_names:
        try:
            columns = inspector.get_columns(table_name)
            col_details = []
            for col in columns:
                col_type = str(col['type'])
                col_details.append(f"{col['name']} ({col_type})")
            
            # Show all columns for validation purposes
            col_list = ', '.join(col_details)
            lines.append(f"- {table_name}: {col_list}")
        except Exception as e:
            # Skip tables that cause issues to prevent memory problems
            logging.warning(f"Skipping table {table_name}: {e}")
            continue
    
    return "\n".join(lines)

@lru_cache(maxsize=1)
def get_valid_tables_and_columns():
    """
    Returns a dictionary of valid tables and their columns for strict validation.
    """
    engine = get_db_engine()
    inspector = inspect(engine)
    valid_schema = {}
    
    try:
        table_names = sorted(inspector.get_table_names())
        for table in table_names:
            try:
                columns = inspector.get_columns(table)
                valid_schema[table] = [col['name'] for col in columns]
            except Exception as e:
                logging.warning(f"Skipping table {table}: {e}")
                continue
    except Exception as e:
        logging.error(f"Error getting valid schema: {e}")
    
    return valid_schema

@lru_cache(maxsize=1) 
def get_join_guides():
    """
    Returns a list of join relationships in the format:
    - table1.column1 → table2.column2
    """
    engine = get_db_engine()
    inspector = inspect(engine)
    join_lines = []
    
    try:
        table_names = sorted(inspector.get_table_names())
        for table in table_names:
            try:
                for fk in inspector.get_foreign_keys(table):
                    if fk['referred_table'] and fk['referred_columns'] and fk['constrained_columns']:
                        join_lines.append(
                            f"- {table}.{fk['constrained_columns'][0]} → {fk['referred_table']}.{fk['referred_columns'][0]}"
                        )
            except Exception as e:
                # Skip problematic foreign keys
                logging.warning(f"Skipping foreign keys for table {table}: {e}")
                continue
    except Exception as e:
        logging.error(f"Error getting join guides: {e}")
    
    return "\n".join(join_lines)

# Usage in your prompt:
def create_custom_prompt():
    schema = get_schema_summary()
    return f"""
You are an expert SQL developer assistant for a farming system.

Database schema:
{schema}

Important Rules:
1. Always return your final answer as a single JSON object with 'query', 'data', and 'analysis' keys.
2. For time series, group by date_trunc('month', date_column).
3. Include error handling in your response.
4. When referring to a chiller, always use its name (from users_chiller.name) not its ID. Join users_farmer.chiller_id to users_chiller.id to get the name.
5. Do not output any explanation, thoughts, or logs—only the JSON object as your final answer.

Response format:
{{
    "query": "SELECT ...",
    "data": [{{"column1": value1, ...}}],
    "analysis": {{
        "mean": 0.0,
        "median": 0.0,
        "max": 0.0,
        "min": 0.0,
        "insights": "Text analysis"
    }}
}}
"""