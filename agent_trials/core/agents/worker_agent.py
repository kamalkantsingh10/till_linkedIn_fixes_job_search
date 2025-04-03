import yaml
import inspect
import functools
import re
from typing import List, Dict, Any, Callable, Optional, Union, Type
from enum import Enum
import json
from pydantic import BaseModel, Field

# Import LangChain components
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

# Import your model utility
from framework.core.brains import Models, get_model


# Define output schemas for parsing
class ToolCall(BaseModel):
    """Schema for a single tool call"""
    tool_name: str = Field(description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(description="Parameters to pass to the tool")


class AgentPlan(BaseModel):
    """Schema for the agent's plan"""
    reasoning: str = Field(description="The agent's reasoning about the plan")
    missing_info: Optional[str] = Field(None, description="Information that is missing but required")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tools to call in sequence")
    final_answer: Optional[str] = Field(None, description="Final answer if no tool calls are needed")


class WorkerAgent:
    """Base worker agent class that handles function discovery and execution"""
    
    def __init__(self, config_file: str, model: Union[str, Models] = Models.GPT4o):
        # Load configuration from YAML
        self.config = self._load_config(config_file)
        
        # Extract key parameters from config
        self.personality = self.config.get("personality", "")
        self.primary_goals = self.config.get("primary_goals", "")
        self.capabilities = self.config.get("capabilities", "")
        
        # Set up LLM
        model_name = model.value if isinstance(model, Models) else model
        model_config = self.config.get("llm_settings", {})
        temperature = model_config.get("temperature", 0)
        max_tokens = model_config.get("max_tokens", 4096)
        
        # Get the LLM from your utility function
        if isinstance(model, str) and model in [m.value for m in Models]:
            model = Models(model)
        
        self.llm = get_model(model, temperature, max_tokens)
        
        # Collect all tools/functions with the decorator
        self.available_tools = self._discover_tools()
        
        # Output parser for structured responses
        self.parser = PydanticOutputParser(pydantic_object=AgentPlan)
        
        # Conversation context
        self.context = []
    
    def _load_config(self, config_file: str) -> Dict:
        """Load agent configuration from YAML file"""
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    
    def _discover_tools(self) -> List[Dict]:
        """Automatically discover all methods with @tool_to_call decorator"""
        tools = []
        
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_is_tool') and attr._is_tool:
                # Extract function metadata
                signature = inspect.signature(attr)
                doc = attr.__doc__ or "No description available"
                
                # Get parameter info
                parameters = []
                for param_name, param in signature.parameters.items():
                    if param_name != 'self':
                        param_info = {
                            "name": param_name,
                            "required": param.default == inspect.Parameter.empty,
                            "default": None if param.default == inspect.Parameter.empty else param.default
                        }
                        # Add type hints if available
                        if param.annotation != inspect.Parameter.empty:
                            param_info["type"] = str(param.annotation.__name__)
                        parameters.append(param_info)
                
                # Add function to available tools
                tools.append({
                    "name": attr_name,
                    "description": doc,
                    "parameters": parameters
                })
        
        return tools
    
    def process_request(self, user_request: str) -> str:
        """Process a user request and return a response"""
        try:
            # Build prompt with agent details and tool info
            prompt = self._build_prompt(user_request)
            
            # Get response from LLM
            llm_response = self._call_llm(prompt)
            
            # Parse and execute any function calls
            plan = self._parse_llm_response(llm_response)
            
            # Check if missing information is requested
            if plan.missing_info:
                response = self._format_missing_info(plan.missing_info)
                self.context.append({"user": user_request, "agent": response})
                return response
                
            # Check if there are tool calls to execute
            if plan.tool_calls:
                result = self._execute_function_sequence(plan.tool_calls)
                response = self._format_execution_response(plan, result)
                self.context.append({"user": user_request, "agent": response, "execution": result})
                return response
            else:
                # Just return the final answer if no tool calls
                self.context.append({"user": user_request, "agent": plan.final_answer})
                return plan.final_answer
        
        except Exception as e:
            error_response = f"I encountered an issue while processing your request: {str(e)}"
            self.context.append({"user": user_request, "agent": error_response, "error": str(e)})
            return error_response
    
    def _build_prompt(self, user_request: str) -> str:
        """Build a prompt for the LLM including agent details and available tools"""
        tool_descriptions = self._format_tool_descriptions()
        context_str = self._format_context()
        
        prompt = f"""
You are an AI assistant with the following characteristics:

Personality: {self.personality}

Primary Goals: {self.primary_goals}

Capabilities: {self.capabilities}

You have access to the following tools:
{tool_descriptions}

{f"Previous Conversation:\n{context_str}" if context_str else ""}

Guidelines:
1. When creating a plan, use at most 3 tools in sequence
2. If you need mandatory information that is missing, clearly state what is needed and why
3. If asked to correct a previous plan, identify exactly which parts need to be changed
4. The output of one tool can be used as the input to another tool if compatible

For your response, follow this structure:
1. First, think through the problem and determine what tools (if any) are needed
2. If any mandatory information is missing, explain exactly what information is needed and why
3. Otherwise, create a sequence of tool calls to solve the problem OR provide a direct answer

User Request: {user_request}
"""
        return prompt
    
    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for inclusion in the prompt"""
        descriptions = []
        for tool in self.available_tools:
            params_str = ""
            for p in tool['parameters']:
                param_type = p.get('type', 'any')
                required = p.get('required', False)
                default = p.get('default')
                
                param_desc = f"- {p['name']} ({param_type})"
                if required:
                    param_desc += " (REQUIRED)"
                elif default is not None:
                    param_desc += f" (default: {default})"
                    
                params_str += param_desc + "\n"
                
            tool_desc = f"""
Tool: {tool['name']}
Description: {tool['description']}
Parameters:
{params_str}
"""
            descriptions.append(tool_desc)
        
        return "\n".join(descriptions)
    
    def _format_context(self) -> str:
        """Format conversation context for inclusion in the prompt"""
        formatted = []
        for entry in self.context[-5:]:  # Include only last 5 exchanges to manage context length
            formatted.append(f"User: {entry['user']}")
            formatted.append(f"Agent: {entry['agent']}")
            if 'execution' in entry:
                formatted.append(f"Execution Result: {entry['execution']}")
        
        return "\n".join(formatted)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt using LangChain"""
        messages = [
            SystemMessage(content=prompt),
        ]
        
        response = self.llm.invoke(messages)
        
        # Extract content based on different possible return types
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, AIMessage):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def _parse_llm_response(self, response: str) -> AgentPlan:
        """Parse the LLM response into a structured format"""
        # Try to extract structured content if the LLM has formatted its response as JSON
        try:
            # Check if there's a JSON block in the response
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
                parsed_json = json.loads(json_str)
                return AgentPlan.parse_obj(parsed_json)
            
            # If response already has a clear structure with tool_calls, parse it
            if "tool_calls" in response:
                # Try to parse as JSON directly
                try:
                    return AgentPlan.parse_raw(response)
                except:
                    pass
            
            # Fallback: Extract components from text response
            reasoning = ""
            missing_info = None
            tool_calls = []
            final_answer = response
            
            # Check for missing information
            missing_info_match = re.search(r'Missing Information:?\s*(.*?)(?:\n\n|\Z)', response, re.DOTALL)
            if missing_info_match:
                missing_info = missing_info_match.group(1).strip()
                
            # Check for reasoning
            reasoning_match = re.search(r'Reasoning:?\s*(.*?)(?:\n\n|\Z)', response, re.DOTALL)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                
            # Check for tool calls
            tool_call_pattern = r'(?:Tool Call|Execute):?\s*(\w+)\s*\n\s*Parameters:?\s*(.*?)(?:\n\n|\Z)'
            tool_matches = re.finditer(tool_call_pattern, response, re.DOTALL)
            
            for match in tool_matches:
                tool_name = match.group(1).strip()
                params_text = match.group(2).strip()
                
                # Parse parameters
                params = {}
                param_matches = re.finditer(r'(\w+):\s*(.*?)(?:\n|\Z)', params_text)
                for param_match in param_matches:
                    param_name = param_match.group(1).strip()
                    param_value = param_match.group(2).strip()
                    params[param_name] = param_value
                
                tool_calls.append(ToolCall(tool_name=tool_name, parameters=params))
            
            # If we found tool calls, remove them from the final answer
            if tool_calls:
                final_answer = None
            
            return AgentPlan(
                reasoning=reasoning,
                missing_info=missing_info,
                tool_calls=tool_calls,
                final_answer=final_answer
            )
            
        except Exception as e:
            # If parsing fails, just return the response as the final answer
            return AgentPlan(
                reasoning="Failed to parse structured response",
                missing_info=None,
                tool_calls=[],
                final_answer=response
            )
    
    def _format_missing_info(self, missing_info: str) -> str:
        """Format the response when missing information is identified"""
        template = self.config.get("missing_info_template", 
                                   "I need additional information: {missing_info}")
        
        if "{missing_info}" in template:
            return template.format(missing_info=missing_info)
        else:
            return f"{template} {missing_info}"
    
    def _execute_function_sequence(self, tool_calls: List[ToolCall]) -> Dict:
        """Execute a sequence of tool calls"""
        results = []
        intermediate_result = None
        
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call.tool_name
            parameters = tool_call.parameters
            
            # Check if tool exists
            if not hasattr(self, tool_name) or not hasattr(getattr(self, tool_name), '_is_tool'):
                results.append({
                    "tool": tool_name,
                    "status": "error",
                    "error": f"Tool '{tool_name}' not found"
                })
                continue
            
            tool_method = getattr(self, tool_name)
            
            # Check if we should pass the previous result as input
            if intermediate_result is not None and i > 0:
                # Try to find a parameter that matches the type of the previous result
                for param_name, param_value in parameters.items():
                    if param_value == "{previous_result}" or param_value == "{{previous_result}}":
                        parameters[param_name] = intermediate_result
            
            try:
                # Execute the tool with the provided parameters
                result = tool_method(**parameters)
                intermediate_result = result
                
                results.append({
                    "tool": tool_name,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "execution_results": results,
            "final_result": intermediate_result
        }
    
    def _format_execution_response(self, plan: AgentPlan, execution_result: Dict) -> str:
        """Format the response after executing tool calls"""
        # Extract the final result and check for errors
        results = execution_result.get("execution_results", [])
        final_result = execution_result.get("final_result")
        
        # Check if any tool execution failed
        errors = [r for r in results if r.get("status") == "error"]
        
        if errors:
            # Format error message
            error_msg = "I encountered issues while executing the plan:\n\n"
            for err in errors:
                error_msg += f"- When using {err['tool']}: {err['error']}\n"
            
            return error_msg
        
        # Default response with the execution result
        response = "I've executed the plan successfully.\n\n"
        
        if plan.reasoning:
            response += f"Based on my reasoning: {plan.reasoning}\n\n"
        
        # Add summary of what was done
        response += "Here's what I did:\n"
        for i, result in enumerate(results):
            response += f"{i+1}. Used {result['tool']} "
            
            # Summarize the parameters used
            tool_call = plan.tool_calls[i] if i < len(plan.tool_calls) else None
            if tool_call:
                params_summary = ", ".join([f"{k}={v}" for k, v in tool_call.parameters.items()])
                response += f"with {params_summary}\n"
            else:
                response += "\n"
        
        response += f"\nFinal result: {final_result}"
        
        return response


# Decorator for marking methods as callable tools
def tool_to_call(func):
    """Decorator to mark a method as an available tool for the agent"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    
    wrapper._is_tool = True
    return wrapper