from agent_trials.core.agents.worker2 import Worker
from framework.core.brains import get_model, tool_to_call, Models
from from 
from dotenv import load_dotenv
import os


def main():
    # Create worker instance with everything included
    
    llm= get_model(Models.QWQ )
    worker = Worker(llm=llm)
    
    # Run example queries
    queries = [
        "What's the weather like in Tokyo? then calculate 25 + 75"
    ]
    
    print("Starting tool-binding runs:")
    print("-" * 50)
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = worker.run_query(query)
        print(f"Response: {response}")
        print("-" * 50)



def main2():
    ae= planning()
    message= ae.invoke({"messages": [("user", "What's the weather like in Tokyo? then calculate 25 + 75")]})
    print(message)
    

if __name__ == "__main__":
    main2()
    
    
    
    """
    open AI-
    
    """