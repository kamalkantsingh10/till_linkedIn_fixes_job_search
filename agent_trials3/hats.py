from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.groq import GroqModel
from typing import Union, List


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""

    response: str= Field (description="the final answer to the user's query.")


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


def llm_ollama(name:str)->OpenAIModel:
    return OpenAIModel(
    model_name=name, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
) 

class Output(BaseModel):
    rephrased_short_question:str = Field
    answer_short_points:str



def doer_hat (model, tools)->Agent:
    doer =Agent(
        model=model,
        system_prompt=(
            "you are a helpful assistant. Be concise reply with one sentence. If you can't find answer even after retries just say you can't find the answer."
        ),
        result_type=Output,
        tools=tools
    )
    return doer


def planner_hat(model, tools)->Agent:
    str_tools =  formatted_tool = "\n\n".join([
            f"{fn.name}: {fn.description.strip()}" for fn in tools
        ])
    
    
    planner = Agent(
        model=model,
        system_prompt=(
            f"""For the given objective, come up with a simple step by step execution plan. \
This plan should involve individual tasks including the tool name, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
    tools you can use:
    {str_tools}
    """
        ),
        result_type=Plan,
        tools=[],
        model_settings={"parallel_tool_calls":False},
        result_retries=5
    )    
    
    return planner

def replanner_hat(model,tools)->Agent:
    str_tools =  formatted_tool = "\n\n".join([
            f"{fn.name}: {fn.description.strip()}" for fn in tools
        ])
    
    replanner = Agent(
        model=model,
        system_prompt=(
            f"""For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

    
    you have only following tools at disposal
    {str_tools} 
    """
        ),
        result_type=Act,
        model_settings={"parallel_tool_calls":False},
        result_retries=5
    )
    
    return replanner

