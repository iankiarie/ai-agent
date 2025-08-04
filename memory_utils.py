"""
Memory optimization utilities for the AI agent
"""
import gc
import os
import logging
import sys
import asyncio
from functools import wraps

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - using fallback memory monitoring")

def memory_cleanup(func):
    """Decorator to force garbage collection after function execution"""
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                gc.collect()
                return result
            except Exception as e:
                gc.collect()
                raise e
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                gc.collect()
                return result
            except Exception as e:
                gc.collect()
                raise e
        return sync_wrapper

def get_memory_usage():
    """Get current memory usage in MB with accurate psutil monitoring"""
    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert bytes to MB
        except Exception as e:
            logging.warning(f"Failed to get psutil memory info: {e}")
    
    # Fallback: estimate using gc stats
    return len(gc.get_objects()) * 0.001  # Rough estimate

def get_detailed_memory_info():
    """Get detailed memory information if psutil is available"""
    if not PSUTIL_AVAILABLE:
        return {"error": "psutil not available"}
    
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": memory_percent,
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "total_mb": psutil.virtual_memory().total / 1024 / 1024
        }
    except Exception as e:
        return {"error": str(e)}

def log_memory_usage(operation_name="", detailed=False):
    """Log current memory usage with optional detailed information"""
    try:
        memory_mb = get_memory_usage()
        
        if detailed and PSUTIL_AVAILABLE:
            info = get_detailed_memory_info()
            if "error" not in info:
                logging.info(
                    f"Memory usage {operation_name}: {memory_mb:.2f} MB "
                    f"(RSS: {info['rss_mb']:.2f} MB, VMS: {info['vms_mb']:.2f} MB, "
                    f"Process: {info['percent']:.1f}%)"
                )
            else:
                logging.info(f"Memory usage {operation_name}: {memory_mb:.2f} MB")
        else:
            logging.info(f"Memory usage {operation_name}: {memory_mb:.2f} MB")
        
        # Warning if approaching 512MB limit
        if memory_mb > 400:
            logging.warning(f"🚨 High memory usage detected: {memory_mb:.2f} MB - approaching 512MB limit!")
        elif memory_mb > 300:
            logging.info(f"⚠️  Moderate memory usage: {memory_mb:.2f} MB")
            
    except Exception as e:
        logging.info(f"Memory monitoring {operation_name}: Unable to get exact usage ({e})")

def force_cleanup():
    """Force garbage collection and cleanup with detailed logging"""
    before_mb = get_memory_usage()
    gc.collect()
    after_mb = get_memory_usage()
    freed_mb = before_mb - after_mb
    
    if freed_mb > 0:
        logging.info(f"🧹 Garbage collection freed {freed_mb:.2f} MB (before: {before_mb:.2f} MB, after: {after_mb:.2f} MB)")
    else:
        logging.info(f"🧹 Garbage collection completed (memory: {after_mb:.2f} MB)")
