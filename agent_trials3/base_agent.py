from agent_trials3.displays.console_based import AgentDisplay
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated, List, Tuple, Literal, Union
import operator
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.groq import GroqModel
from agent_trials3.hats import planner_hat, replanner_hat, doer_hat, Response
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool
from pydantic_ai.exceptions import UsageLimitExceeded
import inspect
import re


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


# Decorators for tools
def tool_for_doer(fn):
    fn._is_tool = True
    fn._use_context = False
    return fn


def tool_for_doer_with_context(fn):
    fn._is_tool = True
    fn._use_context = True
    return fn


class base_agent:
    def __init__(self, llm_think, llm_do, llm_interact):
        # Initialize the display
        self.display = AgentDisplay()
        self.display.start()
        
        # Step 1: get the tools
        tools_at_disposal = self._get_tool_methods()
        
        # Step 2: get the various types of hats for the agents
        self.doer = doer_hat(model=llm_do, tools=tools_at_disposal)
        self.planner = planner_hat(model=llm_think, tools=tools_at_disposal)
        self.replanner = replanner_hat(model=llm_think, tools=tools_at_disposal)
        self.llm_interact = llm_interact
        
        # Step 3: set up agent
        self.app = self.initialize_agent()
        
        # Update display with initialization information
        self.display.thinking("Agent initialized with models and tools")
    
    def get_app(self):
        return self.app
    
    async def execute_step(self, state: PlanExecute):
        # Step 1 - get the full plan from the state
        plan = state["plan"]
        past_steps = state.get("past_steps", [])
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        
        # Update the steps display
        self.display.update_steps(past_steps, plan)
        
        # Step 2 - get the current step to execute
        task = plan[0]
        
        # Step 3 - get the prompt
        task_formatted = f"execute this step {1}, {task} and report answer in human readable answer. if you face a problem just report the error if you can"
        
        # Log to thinking display
        self.display.thinking(f"Executing step: {task}")
        
        # Step 4 - Now Execute the first step
        try:
            response = await self.doer.run(task_formatted)
            
            # Check if this is a function call and extract info
            function_match = re.search(r"([\w_]+)\((.*?)\)", task)
            if function_match:
                function_name = function_match.group(1)
                params_str = function_match.group(2)
                params = {}
                try:
                    # Simple parsing for parameters
                    for param in params_str.split(','):
                        if ':' in param:
                            k, v = param.split(':', 1)
                            params[k.strip()] = v.strip()
                        elif '=' in param:
                            k, v = param.split('=', 1)
                            params[k.strip()] = v.strip()
                except:
                    params = {"raw": params_str}
                
                # Log the function call to the display
                self.display.function(
                    function_name, 
                    params, 
                    response.data.answer_short_points
                )
            
            # Step 5 - Now add the value to previous messages in state
            return {
                "past_steps": past_steps + [(task, response.data.answer_short_points)]
            }
            
        except UsageLimitExceeded as e:
            error_msg = f"Usage limit exceeded: I tried {self.doer._max_result_retries} times but could not get answer"
            self.display.error(error_msg)
            return {
                "past_steps": past_steps + [(task, error_msg)]
            }
        except Exception as e:
            error_msg = f"Error executing {task}: {str(e)}"
            self.display.error(error_msg)
            return {
                "past_steps": past_steps + [(task, error_msg)]
            }

    async def plan_step(self, state: PlanExecute):
        # Update the input display
        self.display.input(state["input"])
        
        # Log to thinking display
        self.display.thinking(f"Planning steps for input: {state['input']}")
        
        # Step 1 - generate the plan
        plan = await self.planner.run(state["input"])
        
        # Log the generated plan to thinking display
        self.display.thinking(f"Generated plan with {len(plan.data.steps)} steps")
        
        # Update the steps display
        self.display.update_steps([], plan.data.steps)
        
        # Step 2 - return the plan
        return {"plan": plan.data.steps}

    async def replan_step(self, state: PlanExecute):
        # Log to thinking display
        self.display.thinking("Replanning based on executed steps...")
        
        # Step 1 - get the new plan
        replan_input = f"""Your objective was this:
        {state["input"]}

        Your original plan was this:
        {state["plan"]}

        You have currently done the follow steps:
        {state["past_steps"]}"""
        
        try:
            output = await self.replanner.run(replan_input)
            
            # Log the replan result to thinking display
            self.display.thinking(f"Replanning complete")
            
            # Step 2 - check if the response is needed from the customer
            if isinstance(output.data.action, Response):
                self.display.thinking(f"Final response determined")
                return {"response": output.data.action}
            else:
                new_plan = output.data.action.steps
                self.display.thinking(f"New plan with {len(new_plan)} steps")
                self.display.update_steps(state.get("past_steps", []), new_plan)
                return {"plan": new_plan}
                
        except Exception as e:
            error_msg = f"Error in replanning: {str(e)}"
            self.display.error(error_msg)
            return {"plan": state["plan"]}

    async def interact_step(self, state: PlanExecute):
        pass

    def should_end(self, state: PlanExecute):
        self.display.thinking("Checking if execution should end")
        if "response" in state and state["response"]:
            self.display.thinking("Execution complete with final response")
            return END
        else:
            self.display.thinking("Continuing execution with next step")
            return "do step"
    
    # We setup a new graph now
    def initialize_agent(self):
        # Step 1 - initiate a workflow
        workflow = StateGraph(PlanExecute)
        
        # Step 2 - add nodes
        workflow.add_node("first plan", self.plan_step)
        workflow.add_node("do step", self.execute_step)
        workflow.add_node("adjust plan", self.replan_step)
        
        # Step 3 - add edges
        workflow.add_edge(START, "first plan")
        workflow.add_edge("first plan", "do step")
        workflow.add_edge("do step", "adjust plan")
        workflow.add_conditional_edges(
            "adjust plan",
            self.should_end,
            ["do step", END]
        )
        
        # Log graph construction to thinking display
        self.display.thinking("Agent workflow graph initialized")
        
        # Step 4 - compile and return
        app = workflow.compile()
        return app
    
    def _get_tool_methods(self):
        tool_funcs = []
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_tool"):
                if method._use_context:
                    tool_funcs.append(Tool(method))  # with RunContext
                else:
                    tool_funcs.append(Tool(method))  # no RunContext
        return tool_funcs
    
    @tool_for_doer
    def calculate(self, expression: str) -> str:
        """Evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The result of the calculation
        """
        self.display.thinking(f"Calculating expression: {expression}")
        try:
            # Be careful with eval() in production code
            result = eval(expression, {"__builtins__": {}})
            return f"The result of {expression} is {result}"
        except Exception as e:
            error_msg = f"Error calculating '{expression}': {str(e)}"
            self.display.error(error_msg)
            return error_msg

    @tool_for_doer
    def get_weather(self, location: str) -> str:
        """Get the current weather for a location.
        
        Args:
            location: The location to get weather for
            
        Returns:
            The current weather information
        """
        self.display.thinking(f"Getting weather for location: {location}")
        # In a real implementation, this would call a weather API
        weather_data = {
            "new york": "72°F, Partly Cloudy",
            "san francisco": "65°F, Foggy",
            "london": "60°F, Rainy",
            "tokyo": "78°F, Sunny",
            "paris": "68°F, Clear",
        }
        location_lower = location.lower()
        if location_lower in weather_data:
            return f"Current weather in {location.title()}: {weather_data[location_lower]}"
        return f"Weather information not available for {location}"
    
    @tool_for_doer
    def search_database(self, query: str) -> str:
        """Search a database for information about a given query.
        
        Args:
            query: The search query string
            
        Returns:
            Information retrieved from the database
        """
        self.display.thinking(f"Searching database for: {query}")
        # In a real implementation, this would query a database
        db_results = {
            "python": "Python is a high-level programming language known for its readability and versatility.",
            "langchain": "LangChain is a framework for developing applications powered by language models.",
            "tools": "Tools in LangChain allow language models to interact with external systems.",
            "england": "England is a country that is part of the United Kingdom. Its capital is London.",
        }
        query_lower = query.lower()
        if query_lower in db_results:
            return db_results[query_lower]
        return f"No information found for query: {query}"


