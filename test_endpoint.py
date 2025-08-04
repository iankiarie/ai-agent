import asyncio
import json
from main import app
from models import AIRequest

async def test_query_endpoint():
    """Test that the query endpoint works correctly"""
    print("🧪 Testing /query endpoint...")
    
    try:
        # Import the query function directly
        from main import query_ai
        
        # Create a test request
        test_request = AIRequest(
            user_id=1,
            query="Hello, how are you?",
            chiller_id=None,
            history=[]
        )
        
        # Test the async function
        result = await query_ai(test_request)
        
        print(f"✅ Query endpoint works! Response type: {type(result)}")
        print(f"✅ Response has text: {'text' in result}")
        print(f"✅ Response text: {result.get('text', 'No text field')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Query endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    await test_query_endpoint()

if __name__ == "__main__":
    asyncio.run(main())
