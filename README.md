# Ketha AI Agent

Ketha AI Agent is an intelligent backend service for answering natural language questions about your farm business data. It uses a combination of LLMs (Anthropic Claude via AWS Bedrock), LangChain, and your PostgreSQL database to provide accurate, context-aware answers, reports, and visualizations.

---

## Features

- **Natural Language to SQL:** Converts user questions into SQL queries using an LLM agent, executes them, and returns results.
- **Automatic Schema Discovery:** Reads your live database schema and join relationships at runtime.
- **Chiller/Farmer/User Name Resolution:** Always refers to chillers, farmers, and users by name (not ID) unless the user explicitly asks for the ID.
- **Contextual Answers:** Uses recent conversation history for more relevant responses.
- **Fallback to General AI:** If a question is not about your data, falls back to general LLM knowledge.
- **Error Handling:** Logs all backend errors but only returns user-friendly messages to the frontend.
- **Session Management:** Maintains per-user conversation history.
- **Data Analysis & Visualization:** Returns tabular data, summary statistics, and chart configs for visualization.

---

## How It Works

### 1. **User Query**

- The frontend sends a POST request to `/query` with:
  - `user_id`: Unique user identifier
  - `query`: The user's question in natural language
  - `chiller_id`: (Optional) The chiller context for filtering
  - `history`: (Optional) Recent conversation turns

### 2. **Routing**

- The backend (`main.py`) uses keyword and pattern matching (`needs_db_query`) to decide:
  - **Database Query:** If the question is about your data (e.g., "What is my chiller name?"), it routes to the SQL agent.
  - **General AI:** Otherwise, it uses the LLM for a general answer.

### 3. **SQL Agent**

- The agent (`sql_agent.py`) is built with LangChain and Anthropic Claude.
- It reads your live database schema and join relationships using SQLAlchemy.
- The agent prompt enforces rules:
  - Always use names, not IDs, for chillers, farmers, and users.
  - Always join tables correctly.
  - Only use IDs if the user explicitly asks.
  - Never use `SELECT *`; always specify columns.
  - Use correct date/time handling and grouping.
- The agent generates a SQL query, executes it, and formats the results.

### 4. **Response Formatting**

- Results are formatted as:
  - **Text answer** (e.g., "Your chiller name is Nutrinuts Bura.")
  - **Tabular data** (if applicable)
  - **Summary statistics** (mean, median, etc.)
  - **Chart config** (for visualization)
- If an error occurs, it is logged, and a generic error message is returned to the user.

### 5. **Session & History**

- Each user's conversation is stored in memory for context.
- The last 4 turns are used to provide context to the agent.

---

## File Structure

```
ketha-ai-agent/
│
├── main.py           # FastAPI app, routing, session, error handling
├── ai_utils.py       # Core logic: routing, formatting, error handling
├── sql_agent.py      # LangChain SQL agent, schema/joins, prompt rules
├── database.py       # SQLAlchemy DB connection and query execution
├── models.py         # Pydantic models for request/response
├── requirements.txt  # Python dependencies
└── ...
```

---

## Setup & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Set up your `.env` file with:
     ```
     DATABASE_URL=postgresql://user:password@host:port/dbname
     AWS_REGION=...
     AWS_ACCESS_KEY_ID=...
     AWS_SECRET_ACCESS_KEY=...
     ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Test the API:**
   - POST to `http://localhost:8000/query` with a JSON body:
     ```json
     {
       "user_id": "user123",
       "query": "What is my chiller name?",
       "chiller_id": 2
     }
     ```

---

## Customization

- **Schema/Join Rules:** The agent always uses the live schema and join info. To add more rules, edit the prompt in `sql_agent.py`.
- **Error Handling:** All backend errors are logged; users only see friendly messages.
- **Session Storage:** By default, session history is in memory. For production, use Redis or a database.

---

## Troubleshooting

- **Agent returns wrong columns or joins:**  
  Ensure your database schema is up-to-date and accessible. The agent reads the schema at runtime.
- **Agent returns IDs instead of names:**  
  The prompt enforces name usage. If your schema uses different column names for names, update the prompt rules.
- **No response or errors:**  
  Check backend logs for details. All errors are logged with stack traces.

---

## Security

- **Never expose your API keys or database credentials.**
- **CORS is set to allow all origins for development.** Restrict this in production.

---

## Extending

- Add more tools (e.g., for external APIs) by extending the agent in `sql_agent.py`.
- Add more analysis or visualization logic in `ai_utils.py`.

---

## License

MIT License

---

## Authors

- [Ian Kiarie / Ketha Technologies]

---

## Support

For issues, open a GitHub issue or contact the maintainers.