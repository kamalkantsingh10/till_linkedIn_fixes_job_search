import getpass
import os
import functools
import json
from enum import Enum
from langchain.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import Replicate
from langchain_ollama import ChatOllama
from typing import List, Dict, Any, Callable, Optional

from framework.core.brains import get_model, tool_to_call, Models,standardize_tool_output



class Worker:
    """
    A self-contained Worker class that includes:
    1. The LLM initialization
    2. Tool methods marked with @tool_to_call
    3. Tool binding and execution functionality
    """
    
    def __init__(self, llm):
        """
        Initialize the Worker with a language model.
        
        Args:
            model_name: The name of the OpenAI model to use
        """

        self.llm = llm
        
        # Create a dictionary to store tool functions by name
        self.tool_functions = {}
        
        # Bind all tool methods to the LLM
        self._bind_tools()
    
    def _bind_tools(self):
        """Discover and bind methods marked with @tool_to_call."""
        tools = []
        
        # Look for methods that have the _is_tool marker
        for attr_name in dir(self):
            if attr_name.startswith('__'):
                continue
                
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_is_tool') and attr._is_tool:
                # Get tool name (use method name if not specified)
                name = attr._tool_name or attr_name
                
                # Get tool description (use docstring if not specified)
                description = attr._tool_description
                if description is None and attr.__doc__:
                    description = attr.__doc__.strip()
                
                # Create a Tool from the method
                tool = Tool(
                    name=name,
                    description=description,
                    func=attr
                )
                tools.append(tool)
                
                # Store the function in our dictionary for direct access
                self.tool_functions[name] = attr
        
        print(f"Discovered {len(tools)} tools: {[t.name for t in tools]}")
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(tools)
        
    def run_query(self, query):
        """
        Run a query through the LLM with tools.
        
        Args:
            query: The query string to process
            
        Returns:
            The LLM's response
        """
        # Get the initial response from the LLM
        response = self.llm_with_tools.invoke(query)
        
        # Print the full response for debugging
        print(f"Full response: {response}")
        response2= standardize_tool_output (llm_response=response, provider="ollama")
        print(f"\n\n modified response: {response2}")
        
        # Extract any tool calls from the response - supporting both OpenAI and LangChain formats
        tool_calls = []
        # if 'tool_calls' in response.additional_kwargs:
        #     tool_calls = response.additional_kwargs['tool_calls']
        # elif 'function_call' in response.additional_kwargs:
        #     # Single function call case
        #     tool_calls = [{
        #         'id': 'function_call_id',
        #         'name': response.additional_kwargs['function_call']['name'],
        #         'arguments': response.additional_kwargs['function_call']['arguments']
        #     }]
        
        # If we have tool calls, we need to execute them and provide the results
        # if tool_calls:
        #     print(f"Tool calls detected: {json.dumps(tool_calls)}")
        #     tool_results = []
            
        #     for tool_call in tool_calls:
        #         # Handle both formats of tool calls
        #         if 'function' in tool_call:
        #             # OpenAI format
        #             tool_name = tool_call['function']['name']
        #             try:
        #                 # Parse arguments from JSON string
        #                 args_str = tool_call['function']['arguments']
        #                 tool_args = json.loads(args_str)
        #             except:
        #                 tool_args = {}
        #             tool_id = tool_call['id']
        #         else:
        #             # LangChain format
        #             tool_name = tool_call['name']
        #             tool_args = tool_call.get('args', {})
        #             tool_id = tool_call.get('id', 'tool_call_id')
                
        #         print(f"Executing tool: {tool_name} with args: {tool_args}")
                
        #         # Get the appropriate function from our dictionary
        #         if tool_name in self.tool_functions:
        #             func = self.tool_functions[tool_name]
                    
        #             try:
        #                 # Extract argument value - OpenAI sometimes uses __arg1 for the first argument
        #                 if '__arg1' in tool_args:
        #                     arg_value = tool_args['__arg1']
        #                     result = func(arg_value)
        #                 else:
        #                     # Try to match args to function parameters
        #                     result = func(**tool_args)
                        
        #                 print(f"Tool execution result: {result}")
                        
        #                 tool_results.append({
        #                     "tool_call_id": tool_id,
        #                     "role": "tool",
        #                     "name": tool_name,
        #                     "content": str(result)
        #                 })
        #             except Exception as e:
        #                 print(f"Error executing tool: {e}")
        #                 tool_results.append({
        #                     "tool_call_id": tool_id,
        #                     "role": "tool",
        #                     "name": tool_name,
        #                     "content": f"Error: {str(e)}"
        #                 })
        #         else:
        #             print(f"Tool not found: {tool_name}")
            
        #     # If we have results, send them back to the LLM for final response
        #     if tool_results:
        #         print(f"Sending tool results back to LLM: {tool_results}")
                
        #         # Create a conversation with the original query, the response with tool calls, and the tool results
        #         messages = [
        #             {"role": "user", "content": query},
        #             {"role": "assistant", "content": response.content or "", "tool_calls": tool_calls},
        #         ]
                
        #         # Add tool results
        #         for result in tool_results:
        #             messages.append(result)
                
        #         # Get the final response
        #         try:
        #             final_response = self.llm.invoke(messages)
        #             return final_response.content
        #         except Exception as e:
        #             print(f"Error getting final response: {e}")
        #             return f"Error processing tool results: {str(e)}"
        
        # If no tool calls, return the original response
        return response.content
    
    @tool_to_call()
    def search_database(self, query: str) -> str:
        """
        Search a database for information about a given query.
        
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

    @tool_to_call(name="math_calculator", description="Calculate mathematical expressions with +, -, *, /, **, and parentheses.")
    def calculate(self, expression: str) -> str:
        """
        Evaluate a mathematical expression.
        
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

    @tool_to_call()
    def get_weather(self, location: str) -> str:
        """
        Get the current weather for a location.
        
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


