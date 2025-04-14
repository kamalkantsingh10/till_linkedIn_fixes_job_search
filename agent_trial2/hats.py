from langchain import hub
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Union, List
from langchain_core.prompts import ChatPromptTemplate

# Choose the LLM that will drive the agent



class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


def doer_hat (llm, tools):
    prompt = "You are a helpful assistant. Keep your answer short, crisp and to the point. Provide human readable answers."
    doer = create_react_agent(llm, tools, prompt=prompt)
    return doer


def planner_hat(llm, str_tools):
    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
    
    
    you have only following tools at disposal
    {str_tools}

        
    """,
            ),
            ("placeholder", "{messages}"),
        ]
    )
    planner = planner_prompt | llm.with_structured_output(Plan)
    
    return planner


def replanner_hat(llm,str_tools):
    replanner_prompt = ChatPromptTemplate.from_template(
    f"""For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{{input}}

Your original plan was this:
{{plan}}

You have currently done the follow steps:
{{past_steps}}

you have only following tools at disposal
{str_tools}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)


    replanner = replanner_prompt |  llm.with_structured_output(Act)
    
    return replanner