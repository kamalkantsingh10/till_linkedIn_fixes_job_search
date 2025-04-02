import os
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import Replicate
from langchain_ollama import ChatOllama
from enum import Enum

class Models(Enum):
    GPT4o = "gpt-4o"
    LLAMA3x3_70B = "llama-3.1-70b-versatile"
    DEEPSEEK_R1_70B = "deepseek-r1-distill-llama-70b"
    CLAUDE_SONNET = "claude-3-7-sonnet-latest"
    GPT4o_mini = "gpt-4o-mini"
    CLAUDE_HAIKU = "claude-3-5-haiku-latest"
    QWEN_32B = "qwen2.5:32b"
    QWEN_14B = "qwen2.5:14b"
    QWEN_7B = "qwen2.5"
    GRANITE_MOE="granite3-moe:3b"
    PHI4="phi4"
    REPLICATE_MODELS = {
        "llava-13b": "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
        "llava-34b": "yorickvp/llava-v1.6-34b:41ecfbfb261e6c1adf3ad896c9066ca98346996d7c4045c5bc944a79d430f174"
    }

def get_model(model: Models, temperature: float = 0, max_tokens: int = 4096):
    
    if model.value.startswith("llava"):
            return Replicate(
            model=Models.REPLICATE_MODELS[model.value],
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
    elif model.value in [Models.LLAMA3x3_70B.value,Models.DEEPSEEK_R1_70B.value]:
            return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=model.value,
            temperature=temperature,
            max_tokens=max_tokens
            )
    elif model.value in [Models.PHI4.value,Models.GRANITE_MOE.value,Models.QWEN_32B.value, Models.QWEN_14B.value, Models.QWEN_7B.value]:
            return ChatOllama(
            model=model.value,
            temperature=temperature
            )
    raise ValueError(f"Unsupported model: {model}")
