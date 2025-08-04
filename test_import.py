try:
    import main
    print("✅ Main module imported successfully")
except Exception as e:
    import traceback
    print("❌ Import error:")
    traceback.print_exc()
