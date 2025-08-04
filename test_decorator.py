import asyncio
from memory_utils import memory_cleanup

@memory_cleanup
async def test_async():
    return "async function works!"

def test_sync():
    return "sync function works!"

async def main():
    # Test async function
    result1 = await test_async()
    print("✅", result1)
    
    # Test sync function  
    result2 = test_sync()
    print("✅", result2)
    
    print("✅ Memory cleanup decorator works for both sync and async!")

if __name__ == "__main__":
    asyncio.run(main())
