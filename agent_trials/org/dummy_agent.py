import yaml
import inspect
import functools
import json
from typing import List, Dict, Any, Optional, Union, Callable

# LangChain imports for messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import model utility (replace with your actual model utility)
from framework.core.brains import Models, get_model


class PlanAndExecuteAgent:
    """Simple plan-and-execute agent that treats all tools equally"""
    
    def __init__(self, config_file: str, model: str = "gpt-4"):
        # Load configuration
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Setup LLM
        self.llm = get_model(model)
        
        # Initialize state and conversations
        self.state = {}
        self.internal_messages = []
        self.user_messages = []
    
    def add_user_message(self, message: str):
        """Add a user message to both conversation tracks"""
        self.user_messages.append({"role": "user", "content": message})
        self.internal_messages.append(HumanMessage(content=message))
    
    def add_assistant_message(self, message: str):
        """Add an assistant message to both conversation tracks"""
        self.user_messages.append({"role": "assistant", "content": message})
        self.internal_messages.append(AIMessage(content=message))
    
    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        # Add user input to conversations
        self.add_user_message(user_input)
        
        # Create a planning prompt
        planning_prompt = self._create_planning_prompt(user_input)
        
        # Get tool calls from LLM
        messages = [SystemMessage(content=planning_prompt)] + self.internal_messages[-10:]
        response = self.llm.invoke(messages)
        
        # Extract tool calls from response
        tool_calls = self._extract_tool_calls(response.content)
        
        # Execute tool sequence
        result = self._execute_tool_sequence(tool_calls)
        
        # Add assistant response to conversations
        self.add_assistant_message(result)
        return result
    
    def _create_planning_prompt(self, user_input: str) -> str:
        """Create a planning prompt for the LLM"""
        # Get tool descriptions
        tool_descriptions = self._get_tool_descriptions()
        
        # Format current state
        state_str = json.dumps(self.state, indent=2) if self.state else "Empty state"
        
        prompt = f"""
You are a helpful assistant that processes user requests by calling appropriate tools.
Analyze the user request and determine a sequence of tool calls to fulfill it.

AVAILABLE TOOLS:
{tool_descriptions}

CURRENT STATE:
{state_str}

When responding, use the following format for EACH tool call:
```tool
tool_name: name_of_tool
parameters:
  param1: value1
  param2: value2
```

If you need to make multiple tool calls, list them in sequence, each in its own code block.

If you don't need to call any tools, just provide a direct response to the user.
"""
        return prompt
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of all available tools"""
        descriptions = []
        
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_is_tool') and attr._is_tool:
                # Get function signature
                signature = inspect.signature(attr)
                
                # Get parameters
                params = []
                for param_name, param in signature.parameters.items():
                    if param_name != 'self':
                        param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
                        default = "" if param.default == inspect.Parameter.empty else f" (default: {param.default})"
                        params.append(f"  - {param_name}: {param_type}{default}")
                
                # Format description
                description = f"""
Tool: {attr_name}
Description: {attr.__doc__ or 'No description available'}
Parameters:
{chr(10).join(params) if params else '  None'}
"""
                descriptions.append(description)
        
        return "\n".join(descriptions)
    
    def _extract_tool_calls(self, response: str) -> List[Dict]:
        """Extract tool calls from LLM response"""
        tool_calls = []
        
        # Look for tool call blocks in the format:
        # ```tool
        # tool_name: name_of_tool
        # parameters:
        #   param1: value1
        #   param2: value2
        # ```
        import re
        tool_blocks = re.findall(r'```tool\n(.*?)```', response, re.DOTALL)
        
        for block in tool_blocks:
            try:
                # Extract tool name
                tool_match = re.search(r'tool_name:\s*(.*?)$', block, re.MULTILINE)
                if not tool_match:
                    continue
                
                tool_name = tool_match.group(1).strip()
                
                # Extract parameters
                params = {}
                params_match = re.search(r'parameters:\s*(.*?)$', block, re.MULTILINE | re.DOTALL)
                if params_match:
                    params_text = params_match.group(1)
                    
                    # Look for param: value pairs
                    param_matches = re.finditer(r'(\w+):\s*(.*?)$', params_text, re.MULTILINE)
                    for param_match in param_matches:
                        param_name = param_match.group(1).strip()
                        param_value = param_match.group(2).strip()
                        params[param_name] = param_value
                
                tool_calls.append({
                    "tool_name": tool_name,
                    "parameters": params
                })
            except Exception as e:
                # Log the error but continue with other tool calls
                print(f"Error parsing tool call: {e}")
        
        # If no tool blocks were found but there's a direct response
        if not tool_calls and not self._contains_tool_block(response):
            # Treat as a direct response
            self.internal_messages.append(SystemMessage(
                content="LLM decided to respond directly without tool calls."
            ))
            return []
        
        return tool_calls
    
    def _contains_tool_block(self, text: str) -> bool:
        """Check if text contains any tool code blocks"""
        return '```tool' in text
    
    def _execute_tool_sequence(self, tool_calls: List[Dict]) -> str:
        """Execute a sequence of tool calls"""
        if not tool_calls:
            # No tool calls, so just return the LLM's direct response
            return self.internal_messages[-1].content
        
        # Execute each tool in sequence
        execution_summary = []
        final_result = None
        
        for tool_call in tool_calls:
            tool_name = tool_call["tool_name"]
            parameters = tool_call["parameters"]
            
            self.internal_messages.append(SystemMessage(
                content=f"Executing tool: {tool_name} with parameters: {json.dumps(parameters)}"
            ))
            
            # Execute the tool
            try:
                # Get the tool method
                if hasattr(self, tool_name) and hasattr(getattr(self, tool_name), '_is_tool'):
                    tool_method = getattr(self, tool_name)
                    
                    # Prepare parameters (convert types if needed)
                    processed_params = self._process_parameters(tool_method, parameters)
                    
                    # Execute the tool
                    result = tool_method(**processed_params)
                    final_result = result  # Save the last result
                    
                    # Record result in internal conversation
                    self.internal_messages.append(SystemMessage(
                        content=f"Tool result: {json.dumps(result)}"
                    ))
                    
                    # Update state with relevant information from the result
                    if isinstance(result, dict) and result.get("update_state", False):
                        # Tool result indicates state should be updated
                        state_updates = result.get("state_updates", {})
                        for key, value in state_updates.items():
                            self._update_state(key, value)
                    
                    # Add to execution summary
                    execution_summary.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "result": result
                    })
                else:
                    raise ValueError(f"Tool not found: {tool_name}")
            
            except Exception as e:
                # Log the error and continue
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                self.internal_messages.append(SystemMessage(content=error_msg))
                execution_summary.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "error": str(e)
                })
        
        # Generate a final response based on the execution results
        response_prompt = f"""
Based on the tool execution results, generate a final response to the user.

Execution summary:
{json.dumps(execution_summary, indent=2)}

Your response should:
1. Address the user's original request
2. Be conversational and helpful
3. Include relevant information from the tool results
4. Not mention the technical details of tool execution

Generate ONLY the response to the user, with no additional formatting.
"""
        
        # Get final response from LLM
        messages = [SystemMessage(content=response_prompt)] + self.internal_messages[-15:]
        final_response = self.llm.invoke(messages)
        
        return final_response.content
    
    def _process_parameters(self, tool_method: Callable, parameters: Dict) -> Dict:
        """Process and convert parameters to the correct types"""
        processed = {}
        signature = inspect.signature(tool_method)
        
        for param_name, param_value in parameters.items():
            if param_name in signature.parameters:
                param_info = signature.parameters[param_name]
                if param_info.annotation != inspect.Parameter.empty:
                    # Convert to the expected type
                    try:
                        if param_info.annotation == int:
                            processed[param_name] = int(param_value)
                        elif param_info.annotation == float:
                            processed[param_name] = float(param_value)
                        elif param_info.annotation == bool:
                            processed[param_name] = param_value.lower() in ('true', 'yes', '1')
                        else:
                            processed[param_name] = param_value
                    except Exception:
                        # If conversion fails, use the original value
                        processed[param_name] = param_value
                else:
                    processed[param_name] = param_value
            else:
                processed[param_name] = param_value
        
        return processed
    
    # Internal state management methods
    def _update_state(self, key: str, value: Any) -> Dict:
        """Update the agent's state with a key-value pair."""
        self.state[key] = value
        return self.state
    
    def _get_state_value(self, key: Optional[str] = None) -> Any:
        """Get a value from the agent's state."""
        if key is None:
            return self.state
        return self.state.get(key)
    
    # Example tool implementation - add your own tools here
    @tool_to_call
    def search_information(self, query: str) -> Dict:
        """Search for information based on a query.
        
        :param query: The search query
        :return: Search results
        """
        # Simplified implementation for demonstration
        results = {
            "query": query,
            "results": [f"Sample result for {query}"],
            "update_state": True,
            "state_updates": {
                "last_search": query
            }
        }
        return results


# Decorator for marking tools
def tool_to_call(func):
    """Decorator to mark a method as an available tool"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    
    wrapper._is_tool = True
    return wrapper


# Example usage (for your reference)
if __name__ == "__main__":
    # This would be used in your application
    agent = PlanAndExecuteAgent("config.yaml")
    
    # Process a user request
    response = agent.process_input("Tell me about the weather in New York")
    print(f"Assistant: {response}")