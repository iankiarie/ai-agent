"""
Ketha AI Agent Startup Script
Launches the AI agent with enhanced monitoring and dashboard
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables from .env file
load_dotenv()

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("ketha_ai.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "AWS_REGION", 
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print("✅ All required environment variables are set")
    return True

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*60)
    print("🚀 KETHA AI AGENT - ENHANCED MONITORING")
    print("="*60)
    print(f"📍 Main API: http://localhost:8000")
    print(f"📊 Admin Dashboard: http://localhost:8000/admin")
    print(f" Health Check: http://localhost:8000/health")
    print(f"📁 API Docs: http://localhost:8000/docs")
    print("="*60)
    print("🎯 Features:")
    print("  • Real-time memory monitoring")
    print("  • Performance analytics")
    print("  • User activity tracking")
    print("  • Optimization recommendations")
    print("  • Export capabilities")
    print("="*60)
    print("🛠  Management Commands:")
    print("  • POST /cleanup - Manual memory cleanup")
    print("  • POST /clear_conversation - Clear user sessions")
    print("  • GET /admin/export - Export metrics")
    print("="*60)
    print("⚠️  Memory Optimization Active:")
    print("  • 512MB limit monitoring")
    print("  • Automatic garbage collection")
    print("  • Session size limits")
    print("  • Lazy model loading")
    print("="*60 + "\n")

def main():
    """Main startup function"""
    setup_logging()
    
    if not check_environment():
        sys.exit(1)
    
    print_startup_info()
    
    try:
        # Import the main app after environment check
        from main import app
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload in production for memory efficiency
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Ketha AI Agent...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
