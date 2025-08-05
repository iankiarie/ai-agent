"""
Performance Monitor for Ketha AI Agent
Provides advanced performance analytics and optimization insights
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import time
from collections import defaultdict, deque
import logging

class PerformanceMonitor:
    def __init__(self):
        self.db_query_times = deque(maxlen=100)
        self.bedrock_query_times = deque(maxlen=100)
        self.memory_snapshots = deque(maxlen=200)
        self.user_sessions = defaultdict(list)
        self.query_patterns = defaultdict(int)
        self.error_patterns = defaultdict(int)
        self.peak_concurrent_users = 0
        self.lock = threading.Lock()
        
    def log_db_performance(self, query: str, execution_time: float, success: bool):
        """Log database query performance"""
        with self.lock:
            self.db_query_times.append({
                'timestamp': datetime.now(),
                'execution_time': execution_time,
                'success': success,
                'query_type': self._classify_query(query)
            })
    
    def log_bedrock_performance(self, query: str, execution_time: float, success: bool):
        """Log Bedrock API performance"""
        with self.lock:
            self.bedrock_query_times.append({
                'timestamp': datetime.now(),
                'execution_time': execution_time,
                'success': success
            })
    
    def log_user_session(self, user_id: str, action: str):
        """Log user session activity"""
        with self.lock:
            self.user_sessions[user_id].append({
                'timestamp': datetime.now(),
                'action': action
            })
            
            # Track concurrent users
            active_users = len([uid for uid, sessions in self.user_sessions.items() 
                              if sessions and (datetime.now() - sessions[-1]['timestamp']).seconds < 300])
            if active_users > self.peak_concurrent_users:
                self.peak_concurrent_users = active_users
    
    def log_query_pattern(self, query: str):
        """Analyze and log query patterns"""
        pattern = self._extract_pattern(query)
        with self.lock:
            self.query_patterns[pattern] += 1
    
    def log_error_pattern(self, error: str):
        """Log error patterns for analysis"""
        error_type = self._classify_error(error)
        with self.lock:
            self.error_patterns[error_type] += 1
    
    def _classify_query(self, query: str) -> str:
        """Classify SQL query type"""
        query_lower = query.lower().strip()
        if query_lower.startswith('select'):
            if 'join' in query_lower:
                return 'complex_select'
            elif 'group by' in query_lower or 'order by' in query_lower:
                return 'aggregated_select'
            else:
                return 'simple_select'
        elif query_lower.startswith(('insert', 'update', 'delete')):
            return 'modification'
        else:
            return 'other'
    
    def _extract_pattern(self, query: str) -> str:
        """Extract query pattern for analysis"""
        words = query.lower().split()[:5]  # First 5 words
        return ' '.join(words)
    
    def _classify_error(self, error: str) -> str:
        """Classify error type"""
        error_lower = error.lower()
        if 'database' in error_lower or 'sql' in error_lower:
            return 'database_error'
        elif 'bedrock' in error_lower or 'aws' in error_lower:
            return 'bedrock_error'
        elif 'memory' in error_lower or 'out of memory' in error_lower:
            return 'memory_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        else:
            return 'other_error'
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self.lock:
            now = datetime.now()
            
            # DB Performance
            recent_db_queries = [q for q in self.db_query_times if (now - q['timestamp']).seconds < 3600]
            db_avg_time = sum(q['execution_time'] for q in recent_db_queries) / max(len(recent_db_queries), 1)
            db_success_rate = sum(1 for q in recent_db_queries if q['success']) / max(len(recent_db_queries), 1) * 100
            
            # Bedrock Performance
            recent_bedrock_queries = [q for q in self.bedrock_query_times if (now - q['timestamp']).seconds < 3600]
            bedrock_avg_time = sum(q['execution_time'] for q in recent_bedrock_queries) / max(len(recent_bedrock_queries), 1)
            bedrock_success_rate = sum(1 for q in recent_bedrock_queries if q['success']) / max(len(recent_bedrock_queries), 1) * 100
            
            # User Activity
            active_users_count = len([uid for uid, sessions in self.user_sessions.items() 
                                    if sessions and (now - sessions[-1]['timestamp']).seconds < 300])
            
            return {
                'database_performance': {
                    'avg_response_time': db_avg_time,
                    'success_rate': db_success_rate,
                    'total_queries': len(recent_db_queries),
                    'query_types': dict(defaultdict(int, {qtype: sum(1 for q in recent_db_queries if q['query_type'] == qtype) 
                                                        for qtype in set(q['query_type'] for q in recent_db_queries)}))
                },
                'bedrock_performance': {
                    'avg_response_time': bedrock_avg_time,
                    'success_rate': bedrock_success_rate,
                    'total_queries': len(recent_bedrock_queries)
                },
                'user_activity': {
                    'active_users': active_users_count,
                    'peak_concurrent': self.peak_concurrent_users,
                    'total_unique_users': len(self.user_sessions)
                },
                'query_patterns': dict(sorted(self.query_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
                'error_patterns': dict(self.error_patterns)
            }

class OptimizationAnalyzer:
    """Analyzes system performance and suggests optimizations"""
    
    @staticmethod
    def analyze_bottlenecks(performance_data: Dict[str, Any], memory_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze system bottlenecks and suggest optimizations"""
        bottlenecks = []
        
        # Database Performance Analysis
        db_perf = performance_data.get('database_performance', {})
        if db_perf.get('avg_response_time', 0) > 3:
            bottlenecks.append({
                'type': 'database',
                'severity': 'high',
                'issue': 'Slow Database Queries',
                'description': f"Average DB response time is {db_perf.get('avg_response_time', 0):.2f}s",
                'suggestions': [
                    'Add database indexes for frequently queried columns',
                    'Optimize complex JOIN operations',
                    'Consider query result caching',
                    'Review database connection pooling'
                ]
            })
        
        # Memory Analysis
        if memory_stats.get('rss_mb', 0) > 400:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'critical',
                'issue': 'High Memory Usage',
                'description': f"Memory usage is {memory_stats.get('rss_mb', 0):.0f}MB",
                'suggestions': [
                    'Implement more aggressive garbage collection',
                    'Reduce session storage limits',
                    'Optimize DataFrame operations',
                    'Consider streaming large datasets'
                ]
            })
        
        # Bedrock Performance Analysis
        bedrock_perf = performance_data.get('bedrock_performance', {})
        if bedrock_perf.get('avg_response_time', 0) > 5:
            bottlenecks.append({
                'type': 'api',
                'severity': 'medium',
                'issue': 'Slow API Responses',
                'description': f"Average API response time is {bedrock_perf.get('avg_response_time', 0):.2f}s",
                'suggestions': [
                    'Implement response caching for common queries',
                    'Optimize prompt engineering',
                    'Consider parallel processing for batch operations',
                    'Review API rate limiting'
                ]
            })
        
        # Concurrency Analysis
        user_activity = performance_data.get('user_activity', {})
        if user_activity.get('peak_concurrent', 0) > 20:
            bottlenecks.append({
                'type': 'concurrency',
                'severity': 'medium',
                'issue': 'High Concurrent Load',
                'description': f"Peak concurrent users: {user_activity.get('peak_concurrent', 0)}",
                'suggestions': [
                    'Implement request queuing',
                    'Add horizontal scaling capabilities',
                    'Optimize session management',
                    'Consider load balancing'
                ]
            })
        
        return bottlenecks
    
    @staticmethod
    def suggest_optimizations(performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest performance optimizations based on usage patterns"""
        optimizations = []
        
        query_patterns = performance_data.get('query_patterns', {})
        top_patterns = list(query_patterns.keys())[:3]
        
        if top_patterns:
            optimizations.append({
                'category': 'Caching',
                'priority': 'high',
                'title': 'Implement Query Result Caching',
                'description': 'Cache results for the most common query patterns',
                'implementation': [
                    f"Cache results for: {', '.join(top_patterns)}",
                    'Use Redis or in-memory cache with TTL',
                    'Implement cache invalidation strategy'
                ],
                'estimated_improvement': '30-50% response time reduction'
            })
        
        db_perf = performance_data.get('database_performance', {})
        complex_queries = db_perf.get('query_types', {}).get('complex_select', 0)
        
        if complex_queries > 10:
            optimizations.append({
                'category': 'Database',
                'priority': 'medium',
                'title': 'Optimize Complex Queries',
                'description': 'Many complex SELECT queries detected',
                'implementation': [
                    'Create materialized views for common joins',
                    'Add composite indexes',
                    'Consider query result preprocessing'
                ],
                'estimated_improvement': '20-40% database performance'
            })
        
        return optimizations

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
optimization_analyzer = OptimizationAnalyzer()
