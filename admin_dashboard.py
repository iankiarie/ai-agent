"""
Admin Metrics for Ketha AI Agent
Provides performance monitoring and metrics collection
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from memory_utils import get_detailed_memory_info, get_memory_usage
import logging
from collections import defaultdict, deque
import threading

# Optional psutil import with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - using fallback memory monitoring")

class AdminMetrics:
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.query_history = deque(maxlen=max_history)
        self.memory_history = deque(maxlen=max_history)
        self.response_times = deque(maxlen=max_history)
        self.error_count = 0
        self.total_queries = 0
        self.db_queries = 0
        self.bedrock_queries = 0
        self.user_activity = defaultdict(int)
        self.peak_memory = 0
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        
    def log_query(self, user_id: str, query: str, route: str, response_time: float, success: bool):
        with self.lock:
            timestamp = datetime.now()
            self.query_history.append({
                'timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'query': query[:100] + "..." if len(query) > 100 else query,
                'route': route,
                'response_time': response_time,
                'success': success
            })
            
            self.total_queries += 1
            if route == 'database':
                self.db_queries += 1
            else:
                self.bedrock_queries += 1
                
            if not success:
                self.error_count += 1
                
            self.user_activity[user_id] += 1
            self.response_times.append(response_time)
            
    def log_memory(self):
        with self.lock:
            memory_mb = get_memory_usage()
            if memory_mb > self.peak_memory:
                self.peak_memory = memory_mb
                
            self.memory_history.append({
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_mb
            })
            
    def get_stats(self, session_store=None) -> Dict[str, Any]:
        with self.lock:
            uptime = datetime.now() - self.start_time
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            # Get active users count safely
            active_users = 0
            if session_store and hasattr(session_store, 'store'):
                active_users = len(session_store.store)
            elif session_store and isinstance(session_store, dict):
                active_users = len(session_store)
            
            return {
                'uptime_hours': round(uptime.total_seconds() / 3600, 2),
                'total_queries': self.total_queries,
                'db_queries': self.db_queries,
                'bedrock_queries': self.bedrock_queries,
                'error_rate': round((self.error_count / max(self.total_queries, 1)) * 100, 2),
                'avg_response_time': round(avg_response_time, 3),
                'peak_memory': self.peak_memory,
                'current_memory': get_memory_usage(),
                'active_users': active_users,
                'unique_users': len(self.user_activity),
                'queries_per_hour': round(self.total_queries / max(uptime.total_seconds() / 3600, 1), 2)
            }
            
    def get_memory_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.memory_history)
            
    def get_query_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.query_history)

# Global metrics instance
admin_metrics = AdminMetrics()