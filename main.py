from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from ai_utils import handle_db_query, handle_general_query, needs_db_query, is_generic_response
from models import AIRequest, AIResponse
from memory_utils import memory_cleanup, log_memory_usage, force_cleanup, get_detailed_memory_info
import traceback
import logging
import re
from typing import List, Dict, Any
import gc

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use a memory-efficient session store
class LimitedSessionStore:
    def __init__(self, max_users=100, max_history_per_user=10):
        self.store = {}
        self.max_users = max_users
        self.max_history_per_user = max_history_per_user
    
    def get_session(self, user_id):
        if user_id not in self.store:
            if len(self.store) >= self.max_users:
                # Remove oldest user session
                oldest_user = next(iter(self.store))
                del self.store[oldest_user]
                gc.collect()
            self.store[user_id] = []
        return self.store[user_id]
    
    def add_to_session(self, user_id, entry):
        session = self.get_session(user_id)
        session.append(entry)
        # Keep only recent history
        if len(session) > self.max_history_per_user:
            session[:] = session[-self.max_history_per_user:]
    
    def clear_session(self, user_id):
        if user_id in self.store:
            self.store[user_id] = []

session_store = LimitedSessionStore()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

@app.post("/query", response_model=AIResponse)
@memory_cleanup
async def query_ai(request: AIRequest):
    log_memory_usage("before query")
    logging.info(f"Received request: user_id={request.user_id}, query={request.query}, chiller_id={request.chiller_id}")
    user_session = session_store.get_session(request.user_id)
    try:
        # Use history from request if provided, else fallback to session
        history = request.history if request.history else user_session[-4:] if len(user_session) > 0 else []
        if needs_db_query(request.query):
            response = handle_db_query(request.query, chiller_id=request.chiller_id, history=history)
            logging.info(f"AI DB Response: {response}")
            session_store.add_to_session(request.user_id, {"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
            log_memory_usage("after DB query")
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
                session_store.add_to_session(request.user_id, {"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
                log_memory_usage("after fallback DB query")
                return {
                    "text": response.get("final_answer") or response.get("text") or "Here are your results:",
                    "isReport": response.get("isReport", True),
                    "isTable": response.get("isTable", True),
                    **response
                }
            session_store.add_to_session(request.user_id, {"user": request.query, "ai": ai_text})
            log_memory_usage("after general query")
            return {
                "text": ai_text,
                "isReport": False
            }
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Error processing query: {error_trace}")
        force_cleanup()  # Force cleanup on error
        return {
            "text": f"Error processing your query: {str(e)}",
            "isReport": False
        }

@app.post("/clear_conversation")
async def clear_conversation(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    chiller_id = payload.get("chiller_id")  # Not strictly needed for session, but included for completeness
    session_store.clear_session(user_id)
    logging.info(f"Cleared conversation for user_id={user_id}, chiller_id={chiller_id}")
    return {"status": "cleared"}

@app.post("/debug_route")
async def debug_route(payload: dict = Body(...)):
    query = payload.get("query", "")
    route = "db" if needs_db_query(query) else "bedrock"
    return {"route": route}

@app.post("/health")
async def health_check():
    """Health check endpoint with detailed memory status"""
    try:
        log_memory_usage("health check", detailed=True)
        memory_info = get_detailed_memory_info()
        
        status = "healthy"
        if "error" not in memory_info:
            if memory_info["rss_mb"] > 450:
                status = "critical_memory"
            elif memory_info["rss_mb"] > 350:
                status = "high_memory"
        
        return {
            "status": status,
            "memory_optimized": True,
            "memory_info": memory_info
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/cleanup")
async def manual_cleanup():
    """Manual cleanup endpoint for maintenance"""
    try:
        force_cleanup()
        log_memory_usage("after manual cleanup", detailed=True)
        return {
            "status": "cleanup completed",
            "memory_info": get_detailed_memory_info()
        }
    except Exception as e:
        return {"status": "cleanup failed", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)