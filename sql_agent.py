from langchain_community.utilities import SQLDatabase
from langchain_aws import ChatBedrock
from database import get_db_engine
from langchain.chains import create_sql_query_chain
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from sqlalchemy import inspect
from datetime import datetime

def get_sql_agent():
    engine = get_db_engine()
    db = SQLDatabase(engine)
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"temperature": 0.1}
    )

    schema = get_schema_summary()
    joins = get_join_guides()
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt_template = f"""
You are an expert SQL developer assistant for a farming system.

Database schema:
{schema}

Join relationships:
{joins}

Rules:
1. Always use table aliases.
2. Verify column names exist.
3. Use EXTRACT(YEAR FROM date_column) for years.
4. Use DATE_TRUNC('month', date_column) for months.
5. Never use SELECT * - always specify columns.
6. Handle NULL values with COALESCE.
7. For dates, use ISO format: 'YYYY-MM-DD'.
8. If the user specifies a chiller ID, always filter results by that chiller ID (e.g., WHERE chiller_id = <chiller_id>). If not, do not filter by chiller ID.
9. When referring to a chiller, always use its name (from users_chiller.name) not its ID, unless the user explicitly asks for the ID. Join users_farmer.chiller_id to users_chiller.id to get the name.
10. When referring to a farmer, always use their name (from users_user.first_name, surname, or username) not their ID, unless the user explicitly asks for the ID. Join users_farmer.user_id to users_user.id to get the name.
11. When referring to a user, always use their name (from users_user.first_name, surname, or username) not their ID, unless the user explicitly asks for the ID.
12. When presenting results or answers, always refer to chillers, farmers, and users by their names instead of their IDs, unless the user explicitly asks for the ID.
13. If a user question can be answered using the database (e.g., about farmers, milk, chillers, payments, collections, etc.), always use the database and generate a SQL query. Only answer from general knowledge if the question is not about the data in the database.

Current Date: {current_date}

You have access to the following tool:
{{tools}}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, must be: query_sql_db
Action Input: the SQL query string ONLY (without any extra formatting)
Observation: the result of the action
... (this Thought/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT:
- Action Input must contain ONLY the SQL query string
- Do not wrap the query in quotes or any other formatting
- Do not include the tool name in the Action Input

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}
"""

    query_tool = Tool.from_function(
        name="query_sql_db",
        description="Execute SQL queries against the database",
        func=lambda query: db.run(query),
    )
    tools = [query_tool]
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
        max_iterations=5
    )

def get_schema_summary():
    """
    Returns a concise schema summary for all tables in the connected database.
    Example:
    - users_chiller(id, name, location, reference)
    - users_farmer(id, chiller_id, user_id, ...)
    """
    engine = get_db_engine()
    inspector = inspect(engine)
    lines = []
    for table_name in sorted(inspector.get_table_names()):
        columns = inspector.get_columns(table_name)
        col_names = [col['name'] for col in columns]
        # Show up to 6 columns, then ellipsis if more
        if len(col_names) > 6:
            col_list = ', '.join(col_names[:6]) + ', ...'
        else:
            col_list = ', '.join(col_names)
        lines.append(f"- {table_name}({col_list})")
    return "\n".join(lines)

def get_join_guides():
    """
    Returns a list of join relationships in the format:
    - table1.column1 → table2.column2
    """
    engine = get_db_engine()
    inspector = inspect(engine)
    join_lines = []
    for table in sorted(inspector.get_table_names()):
        for fk in inspector.get_foreign_keys(table):
            if fk['referred_table'] and fk['referred_columns'] and fk['constrained_columns']:
                join_lines.append(
                    f"- {table}.{fk['constrained_columns'][0]} → {fk['referred_table']}.{fk['referred_columns'][0]}"
                )
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