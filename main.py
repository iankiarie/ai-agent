from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from models import AIRequest, AIResponse
from memory_utils import memory_cleanup, log_memory_usage, force_cleanup, get_detailed_memory_info
from admin_dashboard import admin_metrics
from enhanced_dashboard import create_enhanced_dashboard_html
from performance_monitor import performance_monitor, optimization_analyzer
import traceback
import logging
import re
import time
import json
from typing import List, Dict, Any
import gc
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import AI utilities with error handling
try:
    from ai_utils import handle_db_query, handle_general_query, needs_db_query, is_generic_response
    AI_ENABLED = True
    logger.info("AI utilities loaded successfully")
except Exception as e:
    logger.error(f"Failed to load AI utilities: {e}")
    AI_ENABLED = False
    
    # Fallback functions when AI is not available
    async def handle_db_query(request):
        return {"text": "Database queries are currently unavailable. Please check configuration.", "error": True}
    
    async def handle_general_query(request):
        return {"text": "AI services are currently unavailable. Please check configuration.", "error": True}
    
    def needs_db_query(query):
        return False
    
    def is_generic_response(response):
        return True

app = FastAPI(title="Ketha AI Agent", description="SQL Agent with Admin Dashboard")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Ketha AI Agent...")
    logger.info(f"AI Services: {'Enabled' if AI_ENABLED else 'Disabled - Check AWS credentials and database'}")
    logger.info("Server startup completed successfully")

@app.on_event("shutdown") 
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Ketha AI Agent is shutting down...")
    # Clean up resources
    gc.collect()
    logger.info("Shutdown completed")

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

# Health check endpoint to ensure service stays alive
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "ai_enabled": AI_ENABLED,
            "memory_mb": get_detailed_memory_info().get("used_mb", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "degraded", "error": str(e)}

@app.get("/")
async def root():
    """Root endpoint - redirect to admin dashboard"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ketha AI Agent</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
                color: white;
                margin: 0;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .container {
                background: rgba(30, 27, 75, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 16px;
                padding: 3rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            h1 { color: #a78bfa; margin-bottom: 1rem; }
            p { color: #cbd5e1; margin-bottom: 2rem; }
            .btn {
                background: linear-gradient(135deg, #8b5cf6, #6366f1);
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                font-weight: 600;
                margin: 0.5rem;
                transition: transform 0.2s;
            }
            .btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Ketha AI Agent</h1>
            <p>Your intelligent SQL agent is running successfully!</p>
            <a href="/admin" class="btn">Access Admin Dashboard</a>
            <a href="/docs" class="btn">API Documentation</a>
        </div>
    </body>
    </html>
    """)

@app.post("/query", response_model=AIResponse)
@memory_cleanup
async def query_ai(request: AIRequest):
    start_time = time.time()
    log_memory_usage("before query")
    logging.info(f"Received request: user_id={request.user_id}, query={request.query}, chiller_id={request.chiller_id}")
    user_session = session_store.get_session(request.user_id)
    
    route_type = "database" if needs_db_query(request.query) else "bedrock"
    success = True
    db_execution_time = 0
    bedrock_execution_time = 0
    
    # Log user activity
    performance_monitor.log_user_session(str(request.user_id), "query_start")
    performance_monitor.log_query_pattern(request.query)
    
    try:
        # Use history from request if provided, else fallback to session
        history = request.history if request.history else user_session[-4:] if len(user_session) > 0 else []
        
        if needs_db_query(request.query):
            db_start = time.time()
            response = handle_db_query(request.query, chiller_id=request.chiller_id, history=history)
            db_execution_time = time.time() - db_start
            
            # Log database performance
            performance_monitor.log_db_performance(request.query, db_execution_time, True)
            
            logging.info(f"AI DB Response: {response}")
            session_store.add_to_session(request.user_id, {"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
            log_memory_usage("after DB query")
            
            # Log memory after processing
            admin_metrics.log_memory()
            
            result = {
                "text": response.get("final_answer") or response.get("text") or "Here are your results:",
                "isReport": response.get("isReport", True),
                "isTable": response.get("isTable", True),
                **response
            }
        else:
            bedrock_start = time.time()
            ai_text = handle_general_query(request.query, history=history)
            bedrock_execution_time = time.time() - bedrock_start
            
            # Log Bedrock performance
            performance_monitor.log_bedrock_performance(request.query, bedrock_execution_time, True)
            
            logging.info(f"AI General Response: {ai_text}")
            if is_generic_response(ai_text):
                logging.info("General response was generic, falling back to DB.")
                
                db_start = time.time()
                response = handle_db_query(request.query, chiller_id=request.chiller_id, history=history)
                db_execution_time = time.time() - db_start
                
                # Log fallback database performance
                performance_monitor.log_db_performance(request.query, db_execution_time, True)
                
                session_store.add_to_session(request.user_id, {"user": request.query, "ai": response.get("final_answer") or response.get("text", "")})
                log_memory_usage("after fallback DB query")
                route_type = "database"  # Update route type for fallback
                result = {
                    "text": response.get("final_answer") or response.get("text") or "Here are your results:",
                    "isReport": response.get("isReport", True),
                    "isTable": response.get("isTable", True),
                    **response
                }
            else:
                session_store.add_to_session(request.user_id, {"user": request.query, "ai": ai_text})
                log_memory_usage("after general query")
                result = {
                    "text": ai_text,
                    "isReport": False
                }
            
            # Log memory after processing
            admin_metrics.log_memory()
        
        response_time = time.time() - start_time
        admin_metrics.log_query(str(request.user_id), request.query, route_type, response_time, success)
        performance_monitor.log_user_session(str(request.user_id), "query_success")
        
        return result
        
    except Exception as e:
        success = False
        response_time = time.time() - start_time
        
        # Log error patterns and performance
        performance_monitor.log_error_pattern(str(e))
        if route_type == "database":
            performance_monitor.log_db_performance(request.query, db_execution_time, False)
        else:
            performance_monitor.log_bedrock_performance(request.query, bedrock_execution_time, False)
        
        admin_metrics.log_query(str(request.user_id), request.query, route_type, response_time, success)
        performance_monitor.log_user_session(str(request.user_id), "query_error")
        
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

# Admin Dashboard Endpoints
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve the enhanced admin dashboard HTML"""
    return create_enhanced_dashboard_html()

@app.get("/admin/metrics")
async def get_admin_metrics():
    """Get comprehensive admin metrics for the dashboard"""
    try:
        # Update memory metrics
        admin_metrics.log_memory()
        
        stats = admin_metrics.get_stats(session_store)
        
        return {
            "stats": stats,
            "memory_history": list(admin_metrics.memory_history),
            "query_history": list(admin_metrics.query_history),
            "user_activity": dict(admin_metrics.user_activity),
            "system_info": get_detailed_memory_info(),
            "session_count": len(session_store.store),
            "recommendations": generate_optimization_recommendations(stats)
        }
    except Exception as e:
        logging.error(f"Error getting admin metrics: {e}")
        return {"error": str(e)}

@app.get("/admin/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        performance_data = performance_monitor.get_performance_summary()
        memory_stats = get_detailed_memory_info()
        
        bottlenecks = optimization_analyzer.analyze_bottlenecks(performance_data, memory_stats)
        optimizations = optimization_analyzer.suggest_optimizations(performance_data)
        
        # Ensure we return comprehensive data even if components are empty
        performance_response = {
            "performance": performance_data if performance_data else {
                "database_performance": {
                    "avg_response_time": 0,
                    "success_rate": 100,
                    "total_queries": 0,
                    "query_types": {}
                },
                "bedrock_performance": {
                    "avg_response_time": 0,
                    "success_rate": 100,
                    "total_queries": 0
                },
                "user_activity": {
                    "active_users": 0,
                    "peak_concurrent": 0,
                    "total_unique_users": 0
                },
                "query_patterns": {}
            },
            "bottlenecks": bottlenecks if bottlenecks else [],
            "optimizations": optimizations if optimizations else [{
                "category": "Status",
                "priority": "info",
                "title": "System Optimal",
                "description": "All systems operating within normal parameters",
                "implementation": ["Continue monitoring", "Maintain current settings"],
                "estimated_improvement": "System stable"
            }],
            "system_health": {
                "memory": memory_stats,
                "uptime": admin_metrics.get_stats(session_store).get("uptime_hours", 0),
                "load": performance_data.get("user_activity", {}).get("active_users", 0),
                "status": "optimal" if memory_stats.get("rss_mb", 0) < 400 else "warning"
            }
        }
        
        return performance_response
    except Exception as e:
        logging.error(f"Error getting performance metrics: {e}")
        return {
            "error": str(e),
            "performance": {
                "database_performance": {"avg_response_time": 0, "success_rate": 100, "total_queries": 0, "query_types": {}},
                "bedrock_performance": {"avg_response_time": 0, "success_rate": 100, "total_queries": 0},
                "user_activity": {"active_users": 0, "peak_concurrent": 0, "total_unique_users": 0},
                "query_patterns": {}
            },
            "bottlenecks": [],
            "optimizations": []
        }

@app.get("/admin/export")
async def export_metrics():
    """Export metrics as JSON for external analysis"""
    try:
        admin_data = await get_admin_metrics()
        performance_data = await get_performance_metrics()
        
        export_data = {
            "export_timestamp": time.time(),
            "admin_metrics": admin_data,
            "performance_metrics": performance_data,
            "system_info": {
                "memory_limit": "512MB",
                "optimization_level": "production",
                "monitoring_active": True
            }
        }
        
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename=ketha-ai-metrics-{int(time.time())}.json"
            }
        )
    except Exception as e:
        return {"error": str(e)}

def generate_optimization_recommendations(stats):
    """Generate optimization recommendations based on current metrics"""
    recommendations = []
    
    if stats['current_memory'] > 450:
        recommendations.append({
            "priority": "critical",
            "title": "Critical Memory Usage",
            "description": "Memory usage is approaching the 512MB limit. Immediate action required.",
            "actions": ["Run manual cleanup", "Restart service", "Check for memory leaks"]
        })
    elif stats['current_memory'] > 350:
        recommendations.append({
            "priority": "high",
            "title": "High Memory Usage",
            "description": "Memory usage is elevated. Monitor closely and consider optimization.",
            "actions": ["Clear old sessions", "Optimize data processing", "Schedule cleanup"]
        })
    
    if stats['avg_response_time'] > 5:
        recommendations.append({
            "priority": "medium",
            "title": "Slow Response Times",
            "description": "Average response time is above optimal threshold.",
            "actions": ["Check database performance", "Optimize queries", "Add caching"]
        })
    
    if stats['error_rate'] > 5:
        recommendations.append({
            "priority": "high",
            "title": "High Error Rate",
            "description": "Error rate is above acceptable threshold.",
            "actions": ["Review error logs", "Fix recurring issues", "Improve error handling"]
        })
    
    if stats['queries_per_hour'] > 100:
        recommendations.append({
            "priority": "medium",
            "title": "High Traffic",
            "description": "Query volume is high. Consider scaling preparations.",
            "actions": ["Monitor performance", "Prepare scaling strategy", "Optimize bottlenecks"]
        })
    
    if len(recommendations) == 0:
        recommendations.append({
            "priority": "info",
            "title": "System Healthy",
            "description": "All metrics are within optimal ranges.",
            "actions": ["Continue monitoring", "Maintain current configuration"]
        })
    
    return recommendations

if __name__ == "__main__":
    try:
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting Ketha AI Agent on port {port}")
        logger.info(f"AI Services: {'Enabled' if AI_ENABLED else 'Disabled'}")
        logger.info(f"Access admin dashboard at: http://localhost:{port}/admin")
        
        # Test critical components before starting
        try:
            test_memory = get_detailed_memory_info()
            logger.info(f"Memory check: {test_memory.get('used_mb', 0)}MB used")
        except Exception as e:
            logger.warning(f"Memory monitoring may be limited: {e}")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            access_log=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error("Check your environment variables and dependencies")
        import traceback
        traceback.print_exc()