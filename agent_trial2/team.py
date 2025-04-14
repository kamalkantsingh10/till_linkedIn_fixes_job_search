import operator
from typing import Annotated, List, Tuple,Literal, Union
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from agent_trial2.tools import tools
from langgraph.graph import END
from langchain_core.prompts import ChatPromptTemplate
from agent_trial2.hats import Response, doer_hat, planner_hat, replanner_hat
from langgraph.graph import StateGraph, START
from langchain.tools import tool
import inspect
import re



class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    
    

class base_agent:
    def __init__(self, llm_think, llm_do, llm_interact):
        
        #step 1: get the tools
        formatted_tool, list_tool =self.__get_tool_info()
        
        #step 2: get the various types of hats for the agents
        self.doer= doer_hat(llm=llm_do, tools=list_tool)
        self.planner= planner_hat(llm=llm_think, str_tools=formatted_tool)
        self.replanner= replanner_hat(llm=llm_think, str_tools=formatted_tool)
        self.llm_interact=llm_interact
        
        #step 3: set up agent
        self.app= self.initialize_agent()
        
    
    def get_app(self):
        return self.app
    
    
    async def execute_step(self,state: PlanExecute):
        #step 1 - get the full plan from the state
        plan= state["plan"]
        plan_str= "\n".join(f"{i+1}. {step}" for i,step in enumerate(plan))
        
        #step 2 - get the current step to execute
        task=plan[0]
        
        #step 3 -  get the prompt
        task_formatted= F""" For the followng plan"
        {plan_str}
        
        you are tasked with executing step {1}, {task}."""
        
        #step 4 - Now Execute the first step- remember the previous steps are being deleted
        response = await self.doer.ainvoke({"messages":[("user", task_formatted)]})
        #step 5 - Now add the value to previous messages in state
        return {
            "past_steps":[(task, response["messages"][-1].content)]
        }


    async def plan_step(self,state: PlanExecute):
        #step 1 - generate the plan
        plan= await self.planner.ainvoke({"messages":["user", state["input"]]})
        
        #step 2 - return the plan
        return {"plan":plan.steps}
        


    async def replan_step(self,state: PlanExecute):
        #step 1 - get the new plan
        output= await self.replanner.ainvoke(state)
        
        #step 2 - check if the response is needed from the customer return
        if isinstance (output.action, Response):
            return{"response": output.action.response}
        else:
            return{"plan":output.action.steps}
            


    async def interact_step(self, state: PlanExecute):
        pass


    def should_end(self, state: PlanExecute):
        if "response" in state and state["response"]:
            return END
        else:
            return "do step"
        
        
    #we setup a new graph now
    def initialize_agent(self):
        
        #step 1 - initiate a workflow
        workflow = StateGraph (PlanExecute)
        
        #step 2 - add nodes
        workflow.add_node("first plan", self.plan_step)
        workflow.add_node("do step", self.execute_step)
        workflow.add_node("adjust plan", self.replan_step)
        
        #step 3 - add edges
        workflow.add_edge(START,"first plan")
        workflow.add_edge("first plan","do step")
        workflow.add_edge("do step", "adjust plan")
        workflow.add_conditional_edges(
            "adjust plan",
            self.should_end,
            ["do step",END]
            )
        
        #step 4 - compile and return
        app= workflow.compile()
        return app
    
    
    def __get_tool_info(self):
        """
        Dynamically identify and return information about all tool-decorated methods.
        
        Returns:
            tuple: (description_string, function_list)
        """
        import inspect
        
        descriptions = ""
        tool_methods = []
        
        # Get the source of the entire class
        try:
            class_source = inspect.getsource(self.__class__)
            
            # Split the source into method chunks
            method_chunks = class_source.split("@tool")
            
            # Skip the first chunk (class definition before any @tool)
            for chunk in method_chunks[1:]:
                # Find the method name
                method_match = inspect.re.search(r'def\s+(\w+)\s*\(', chunk)
                if method_match:
                    method_name = method_match.group(1)
                    
                    # Find the docstring
                    docstring_match = inspect.re.search(r'"""(.*?)"""', chunk, inspect.re.DOTALL)
                    docstring = docstring_match.group(1).strip() if docstring_match else ""
                    
                    # Get the actual method
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        tool_methods.append(method)
                        descriptions += f"{method_name}: {docstring}\n\n"
        except Exception as e:
            # Fallback: Just say what happened, maybe add a more robust solution
            print(f"Error finding tools: {e}")
        
        return descriptions.strip(), tool_methods
        
    
    @tool
    def calculate(self,expression: str) -> str:
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
    def get_weather(self,location: str) -> str:
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
    
    @tool
    def search_database(self,query: str) -> str:
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

    
        
    