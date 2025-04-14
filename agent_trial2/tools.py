from langchain.tools import tool

@tool
def search_database(query: str) -> str:
    """Search a database for information about a given query.
    
    Args:
        query: The search query string
        
    Returns:
        Information retrieved from the database
    """
    print(f"Searching database for: {query}")
    # In a real implementation, this would query a database
    db_results = {
        "python": "Python is a high-level programming language known for its readability and versatility.",
        "langchain": "LangChain is a framework for developing applications powered by language models.",
        "tools": "Tools in LangChain allow language models to interact with external systems.",
    }
    if query.lower() in db_results:
        return db_results[query.lower()]
    return f"No information found for query: {query}"

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        The result of the calculation
    """
    print(f"Calculating: {expression}")
    try:
        # Be careful with eval() in production code
        result = eval(expression, {"__builtins__": {}})
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The location to get weather for
        
    Returns:
        The current weather information
    """
    print(f"Getting weather for: {location}")
    # In a real implementation, this would call a weather API
    weather_data = {
        "new york": "72°F, Partly Cloudy",
        "san francisco": "65°F, Foggy",
        "london": "60°F, Rainy",
        "tokyo": "78°F, Sunny",
    }
    location_lower = location.lower()
    if location_lower in weather_data:
        return f"Current weather in {location.title()}: {weather_data[location_lower]}"
    return f"Weather information not available for {location}"



tools = [search_database, calculate, get_weather]