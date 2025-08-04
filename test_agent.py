from sql_agent import get_sql_agent

if __name__ == "__main__":
    agent = get_sql_agent()
    
    test_queries = [
        "How many milk collections do we have?",
        "Show monthly milk collections for 2025",
        "What's the average payment to farmers?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        response = agent.invoke({"input": query})
        print(f"Response: {response['output']}")
        print(f"{'='*50}")