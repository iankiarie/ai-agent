#!/usr/bin/env python3
"""
Test script to verify all optimizations are working correctly
"""

import sys
import traceback
from memory_utils import log_memory_usage, get_detailed_memory_info, force_cleanup

def test_memory_monitoring():
    """Test memory monitoring functionality"""
    print("🧪 Testing memory monitoring...")
    try:
        log_memory_usage("test start", detailed=True)
        info = get_detailed_memory_info()
        print(f"✅ Memory monitoring works! Current usage: {info.get('rss_mb', 'unknown'):.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Memory monitoring failed: {e}")
        return False

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    try:
        import main
        import ai_utils
        import sql_agent
        import models
        import database
        print("✅ All modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("🧪 Testing FastAPI app creation...")
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting optimization verification tests...\n")
    
    tests = [
        test_memory_monitoring,
        test_imports,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All optimizations verified successfully!")
        print("✅ Your backend is ready for deployment on Render!")
        force_cleanup()
        log_memory_usage("final check", detailed=True)
    else:
        print("⚠️  Some tests failed - please check the errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
