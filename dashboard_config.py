"""
Dashboard Configuration
Customizable settings for the admin dashboard
"""

# Dashboard Settings
DASHBOARD_CONFIG = {
    "refresh_interval": 5000,  # milliseconds
    "memory_warning_threshold": 350,  # MB
    "memory_critical_threshold": 450,  # MB
    "max_memory_limit": 512,  # MB
    "response_time_warning": 3000,  # milliseconds
    "response_time_critical": 5000,  # milliseconds
    "error_rate_warning": 5,  # percentage
    "error_rate_critical": 10,  # percentage
    "max_concurrent_users_warning": 20,
    "max_chart_data_points": 100,
    "max_table_rows": 50,
    "session_timeout": 300,  # seconds (5 minutes)
}

# Performance Monitoring Settings
PERFORMANCE_CONFIG = {
    "db_slow_query_threshold": 3.0,  # seconds
    "bedrock_slow_response_threshold": 5.0,  # seconds
    "memory_sample_interval": 10,  # seconds
    "performance_history_size": 200,
    "query_pattern_tracking": True,
    "error_pattern_tracking": True,
    "user_session_tracking": True,
}

# Optimization Settings
OPTIMIZATION_CONFIG = {
    "auto_cleanup_threshold": 400,  # MB
    "cache_size_limit": 1000,  # number of cached items
    "session_cleanup_interval": 3600,  # seconds (1 hour)
    "enable_lazy_loading": True,
    "enable_gc_optimization": True,
    "enable_session_limits": True,
}

# Alert Settings
ALERT_CONFIG = {
    "enable_memory_alerts": True,
    "enable_performance_alerts": True,
    "enable_error_alerts": True,
    "alert_sound": False,
    "alert_persistence": 30,  # seconds
}

# Export Settings
EXPORT_CONFIG = {
    "include_sensitive_data": False,
    "max_export_history": 10000,  # records
    "export_format": "json",
    "compress_exports": True,
}

# UI Customization
UI_CONFIG = {
    "theme": "gradient",  # gradient, dark, light
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "accent_color": "#27ae60",
    "warning_color": "#f39c12",
    "error_color": "#e74c3c",
    "enable_animations": True,
    "enable_sound_effects": False,
}

def get_dashboard_config():
    """Get dashboard configuration with environment overrides"""
    import os
    
    config = DASHBOARD_CONFIG.copy()
    
    # Allow environment variable overrides
    env_overrides = {
        "DASHBOARD_REFRESH_INTERVAL": "refresh_interval",
        "MEMORY_WARNING_THRESHOLD": "memory_warning_threshold", 
        "MEMORY_CRITICAL_THRESHOLD": "memory_critical_threshold",
        "MAX_MEMORY_LIMIT": "max_memory_limit",
    }
    
    for env_var, config_key in env_overrides.items():
        if os.getenv(env_var):
            try:
                config[config_key] = int(os.getenv(env_var))
            except ValueError:
                pass  # Keep default if conversion fails
    
    return config

def get_performance_config():
    """Get performance monitoring configuration"""
    return PERFORMANCE_CONFIG.copy()

def get_optimization_config():
    """Get optimization configuration"""
    return OPTIMIZATION_CONFIG.copy()

def get_alert_config():
    """Get alert configuration"""
    return ALERT_CONFIG.copy()

def get_export_config():
    """Get export configuration"""
    return EXPORT_CONFIG.copy()

def get_ui_config():
    """Get UI customization configuration"""
    return UI_CONFIG.copy()

# Dashboard feature flags
FEATURE_FLAGS = {
    "enable_enhanced_dashboard": True,
    "enable_performance_monitoring": True,
    "enable_optimization_suggestions": True,
    "enable_real_time_alerts": True,
    "enable_export_functionality": True,
    "enable_user_activity_tracking": True,
    "enable_error_pattern_analysis": True,
    "enable_bottleneck_detection": True,
    "enable_memory_optimization": True,
    "enable_query_caching": False,  # Future feature
    "enable_predictive_scaling": False,  # Future feature
}
