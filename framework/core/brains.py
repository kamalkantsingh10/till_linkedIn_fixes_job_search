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
import re
from langchain_core.output_parsers import JsonOutputToolsParser


class Models(Enum):
    GPT4o = "gpt-4o"
    LLAMA3x3_70B = "llama-3.3-70b-versatile"
    DEEPSEEK_R1_70B = "deepseek-r1-distill-llama-70b"
    CLAUDE_SONNET = "claude-3-7-sonnet-latest"
    GPT4o_mini = "gpt-4o-mini"
    CLAUDE_HAIKU = "claude-3-5-haiku-latest"
    LLAMA3x2_3B= "llama3.2"
    QWEN2x5_CODER_7B= "qwen2.5-coder:latest"
    QWEN2x5_7B= "qwen2.5:latest"
    QWQ = "qwq"


REPLICATE_MODELS = {
    "llava-13b": "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
    "llava-34b": "yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174"
}


def get_model(model: Models, temperature: float = 0, max_tokens: int = 4096):
    if model.value.startswith("llava"):
        return Replicate(
            model=REPLICATE_MODELS[model.value],
            model_kwargs={"temperature": temperature, "max_length": 500, "top_p": 1}
        )
    elif model.value.startswith("claude"):
        return ChatAnthropic(
            model=model.value,
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=max_tokens
        )
    elif model.value.startswith("gpt"):
        return ChatOpenAI(
            model=model.value,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif model.value in [Models.LLAMA3x3_70B.value, Models.DEEPSEEK_R1_70B.value]:
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=model.value,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif model.value in [Models.LLAMA3x2_3B.value, Models.QWQ.value, Models.QWEN2x5_7B.value,Models.QWEN2x5_CODER_7B.value]:
        return ChatOllama(
            model=model.value,
            temperature=temperature
        )
    raise ValueError(f"Unsupported model: {model}")


def tool_to_call(name=None, description=None):
    """
    Custom decorator to mark methods as tools for LLM to call.
    
    Args:
        name: Optional name override for the tool
        description: Optional description override for the tool
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        # Add markers to the function
        wrapper._is_tool = True
        wrapper._tool_name = name
        wrapper._tool_description = description
        return wrapper
    return decorator





def standardize_tool_output(llm_response, provider):
    """
    Standardize tool calling outputs across providers using JsonOutputToolsParser.
    
    Args:
        llm_response: The raw response from the LLM
        provider: String identifying the provider ("openai", "anthropic", or "ollama")
        
    Returns:
        A list of standardized tool calls in the format:
        [
            {
                "name": "tool_name",
                "arguments": {"arg1": "value1", "arg2": "value2"}
            }
        ]
    """
    standardized_calls = []
    
    try:
        # Check for direct tool_calls attribute first (works with newer LangChain versions)
        if hasattr(llm_response, "tool_calls") and llm_response.tool_calls:
            for tool_call in llm_response.tool_calls:
                if isinstance(tool_call, dict):
                    standardized_calls.append({
                        "name": tool_call["name"],
                        "arguments": tool_call["args"]
                    })
                else:
                    # Object format
                    standardized_calls.append({
                        "name": tool_call.name,
                        "arguments": tool_call.args
                    })
            return standardized_calls
        
        # Provider-specific handling
        if provider == "openai":
            # Check additional_kwargs for tool_calls (LangChain format)
            if hasattr(llm_response, "additional_kwargs") and "tool_calls" in llm_response.additional_kwargs:
                for tool_call in llm_response.additional_kwargs["tool_calls"]:
                    standardized_calls.append({
                        "name": tool_call["function"]["name"],
                        "arguments": json.loads(tool_call["function"]["arguments"])
                    })
        
        elif provider == "anthropic":
            # Check for content blocks format
            if hasattr(llm_response, "content") and isinstance(llm_response.content, list):
                for content_block in llm_response.content:
                    if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                        standardized_calls.append({
                            "name": content_block["name"],
                            "arguments": content_block["input"]
                        })
        
        elif provider == "ollama":
            # Try to extract from response content
            if hasattr(llm_response, "content") and isinstance(llm_response.content, str):
                content = llm_response.content
                # Use JsonOutputToolsParser for parsable JSON
                parser = JsonOutputToolsParser()
                try:
                    # The parse method expects JSON string output
                    tool_calls = parser.parse(content)
                    return tool_calls
                except:
                    # If parsing fails, try to extract JSON via regex
                    import re
                    json_match = re.search(r'({.*})', content.replace('\n', ' '))
                    if json_match:
                        tool_call = json.loads(json_match.group(1))
                        standardized_calls.append(tool_call)
        
        return standardized_calls
    
    except Exception as e:
        print(f"Error standardizing tool output: {str(e)}")
        return []