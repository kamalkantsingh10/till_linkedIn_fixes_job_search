import streamlit as st
import asyncio
import re
from typing import List, Tuple, Dict, Any, Optional

from agent_trials3.base_agent import base_agent

class StreamlitAgentDisplay:
    """Handles the Streamlit display for the agent"""
    
    def __init__(self):
        # Initialize session state for various components
        if 'thinking_log' not in st.session_state:
            st.session_state.thinking_log = []
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        if 'function_log' not in st.session_state:
            st.session_state.function_log = []
        if 'current_input' not in st.session_state:
            st.session_state.current_input = ""
        if 'past_steps' not in st.session_state:
            st.session_state.past_steps = []
        if 'plan' not in st.session_state:
            st.session_state.plan = []
        if 'final_response' not in st.session_state:
            st.session_state.final_response = ""

    def thinking(self, message: str):
        """Log a thinking message"""
        st.session_state.thinking_log.append(message)
        # Force refresh (in Streamlit, state updates don't automatically trigger rerenders)
        st.experimental_rerun()

    def error(self, message: str):
        """Log an error message"""
        st.session_state.error_log.append(message)
        st.experimental_rerun()

    def function(self, function_name: str, params: Dict[str, Any], result: str):
        """Log a function call"""
        st.session_state.function_log.append({
            "function": function_name,
            "parameters": params,
            "result": result
        })
        st.experimental_rerun()

    def input(self, message: str):
        """Set the current input"""
        st.session_state.current_input = message
        st.experimental_rerun()

    def update_steps(self, past_steps: List[Tuple], plan: List[str]):
        """Update the steps and plan display"""
        st.session_state.past_steps = past_steps
        st.session_state.plan = plan
        st.experimental_rerun()
        
    def set_final_response(self, response: str):
        """Set the final response"""
        st.session_state.final_response = response
        st.experimental_rerun()
        
    def reset(self):
        """Reset the display"""
        st.session_state.thinking_log = []
        st.session_state.error_log = []
        st.session_state.function_log = []
        st.session_state.current_input = ""
        st.session_state.past_steps = []
        st.session_state.plan = []
        st.session_state.final_response = ""
        st.experimental_rerun()


class StreamlitAgentUI:
    """Streamlit UI wrapper for a base_agent object"""
    
    def __init__(self, agent=None):
        """Initialize the Streamlit UI with an optional base_agent object"""
        self.display = StreamlitAgentDisplay()
        self.agent = agent
        
        if agent:
            # Replace the agent's display with our Streamlit display
            self.agent.display = self.display
            
            # Log initialization
            self.display.thinking("Streamlit UI initialized and connected to agent")
    
    def set_agent(self, agent):
        """Set or update the agent object"""
        self.agent = agent
        self.agent.display = self.display
        self.display.thinking("Agent updated in UI")
    
    def run_app(self):
        """Main function to run the Streamlit UI"""
        # Note: We don't call set_page_config() here anymore
        # It must be called in the main script before creating this object
        
        st.title("🤖 Agent Trials UI")
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            
            # This is where you'd put model selection if needed
            # Or any other configuration options
            
            if self.agent is None:
                st.warning("No agent has been connected yet. Please initialize one first.")
            else:
                st.success("Agent is connected and ready")
            
            if st.button("Reset UI"):
                self.display.reset()
                st.session_state.execution_started = False
                st.success("UI state reset")
        
        # Main content area
        if self.agent is None:
            st.info("Please connect an agent to begin")
        else:
            # User input section
            st.header("✨ What would you like the agent to do?")
            user_input = st.text_area("Enter your request", height=100)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Reset", use_container_width=True):
                    self.display.reset()
                    st.session_state.execution_started = False
                    st.success("Agent state reset")
                    
            with col2:
                if st.button("Execute Request", use_container_width=True, type="primary"):
                    if user_input.strip():
                        st.session_state.execution_started = True
                        
                        # Run the agent with the request
                        try:
                            st.session_state.execution_in_progress = True
                            asyncio.run(self.agent.app.ainvoke({"input": user_input}))
                            st.session_state.execution_in_progress = False
                            st.session_state.execution_complete = True
                        except Exception as e:
                            st.session_state.execution_in_progress = False
                            st.session_state.execution_error = str(e)
                    else:
                        st.warning("Please enter a request")
            
            # Display the agent state
            if 'execution_started' in st.session_state and st.session_state.execution_started:
                self.display_agent_state()

    def display_agent_state(self):
        """Display the current state of the agent"""
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Plan & Progress", "🧠 Agent Thinking", "🛠️ Function Calls", "❌ Errors"])
        
        with tab1:
            st.subheader("Current Request")
            if 'current_input' in st.session_state:
                st.info(st.session_state.current_input)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Completed Steps")
                if 'past_steps' in st.session_state and st.session_state.past_steps:
                    for i, (step, result) in enumerate(st.session_state.past_steps):
                        with st.expander(f"Step {i+1}: {step[:50]}...", expanded=False):
                            st.write(f"**Action:** {step}")
                            st.write(f"**Result:** {result}")
                else:
                    st.write("No steps completed yet")
            
            with col2:
                st.subheader("Upcoming Steps")
                if 'plan' in st.session_state and st.session_state.plan:
                    for i, step in enumerate(st.session_state.plan):
                        st.write(f"{i+1}. {step}")
                else:
                    st.write("No upcoming steps")
            
            if 'final_response' in st.session_state and st.session_state.final_response:
                st.subheader("Final Response")
                st.success(st.session_state.final_response)
        
        with tab2:
            st.subheader("Agent Thinking Log")
            if 'thinking_log' in st.session_state and st.session_state.thinking_log:
                for i, thought in enumerate(st.session_state.thinking_log):
                    st.text(f"[{i+1}] {thought}")
            else:
                st.write("No thinking logged yet")
        
        with tab3:
            st.subheader("Function Calls")
            if 'function_log' in st.session_state and st.session_state.function_log:
                for i, func_call in enumerate(st.session_state.function_log):
                    with st.expander(f"Call {i+1}: {func_call['function']}", expanded=False):
                        st.write(f"**Function:** {func_call['function']}")
                        st.write("**Parameters:**")
                        for param, value in func_call['parameters'].items():
                            st.write(f"- {param}: {value}")
                        st.write(f"**Result:** {func_call['result']}")
            else:
                st.write("No function calls yet")
        
        with tab4:
            st.subheader("Errors")
            if 'error_log' in st.session_state and st.session_state.error_log:
                for i, error in enumerate(st.session_state.error_log):
                    st.error(f"Error {i+1}: {error}")
            else:
                st.write("No errors logged yet")
        
        # Show execution status
        if 'execution_in_progress' in st.session_state and st.session_state.execution_in_progress:
            st.info("Execution in progress...")
        elif 'execution_complete' in st.session_state and st.session_state.execution_complete:
            st.success("Execution complete!")
        elif 'execution_error' in st.session_state:
            st.error(f"Execution failed: {st.session_state.execution_error}")


# Example usage
def main_example():
    """Example of how to use the StreamlitAgentUI"""
    # You must call set_page_config first in your main script
    # st.set_page_config(page_title="Agent Trials UI Demo", layout="wide")
    
    st.title("🤖 Agent Trials UI Demo")
    st.write("This is a demonstration of the Streamlit Agent UI. You need to connect a base_agent object to use it.")
    
    st.info("To use this UI with your agent, import StreamlitAgentUI and create an instance with your agent.")
    
    st.code("""
    from streamlit_agent_ui import StreamlitAgentUI
    
    # IMPORTANT: You must call set_page_config first in your script
    st.set_page_config(page_title="Agent Trials UI", layout="wide")
    
    # Create your agent as normal
    my_agent = base_agent(llm_think, llm_do, llm_interact)
    
    # Create the UI and pass your agent
    ui = StreamlitAgentUI(my_agent)
    
    # Run the UI
    ui.run_app()
    """, language="python")

# This file is meant to be imported, not run directly
# if __name__ == "__main__":
#     st.set_page_config(page_title="Agent Trials UI Demo", layout="wide")
#     main_example()


# Streamlit app for Agent UI
def main():
    st.set_page_config(page_title="Agent Trials UI", layout="wide")
    
    st.title("🤖 Agent Trials UI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        st.write("Select your LLM models")
        
        # Model selection dropdowns
        think_model = st.selectbox(
            "Thinking Model",
            ["OpenAI GPT-4", "Groq Mixtral", "OpenAI GPT-3.5", "Claude 3"],
            index=0
        )
        
        do_model = st.selectbox(
            "Doing Model",
            ["OpenAI GPT-4", "Groq Mixtral", "OpenAI GPT-3.5", "Claude 3"],
            index=2
        )
        
        interact_model = st.selectbox(
            "Interaction Model",
            ["OpenAI GPT-4", "Groq Mixtral", "OpenAI GPT-3.5", "Claude 3"],
            index=2
        )
        
        # Agent initialization button
        if st.button("Initialize Agent"):
            st.session_state.agent_initialized = True
            # In a real implementation, you would initialize the models here
            # For now, we'll just use strings
            st.session_state.agent = base_agent(
                llm_think=think_model,
                llm_do=do_model,
                llm_interact=interact_model
            )
            st.success(f"Agent initialized with the following models:\n- Think: {think_model}\n- Do: {do_model}\n- Interact: {interact_model}")
    
    # Main content area
    if 'agent_initialized' not in st.session_state or not st.session_state.agent_initialized:
        st.info("Please initialize the agent in the sidebar to begin")
    else:
        # User input section
        st.header("✨ What would you like the agent to do?")
        user_input = st.text_area("Enter your request", height=100)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Reset", use_container_width=True):
                if hasattr(st.session_state, 'agent') and hasattr(st.session_state.agent, 'display'):
                    st.session_state.agent.display.reset()
                st.session_state.execution_started = False
                st.success("Agent state reset")
                
        with col2:
            if st.button("Execute Request", use_container_width=True, type="primary"):
                if user_input.strip():
                    st.session_state.execution_started = True
                    # In a real implementation, you would run the agent here
                    # We'll simulate it for now
                    asyncio.run(execute_agent_request(st.session_state.agent, user_input))
                else:
                    st.warning("Please enter a request")
        
        # Display the agent state
        if 'execution_started' in st.session_state and st.session_state.execution_started:
            display_agent_state()

# Function to execute agent request (simulated)
async def execute_agent_request(agent, user_input):
    # In a real implementation, this would call the agent's app
    try:
        st.session_state.execution_in_progress = True
        
        # This will trigger the workflow
        await agent.app.ainvoke({"input": user_input})
        
        st.session_state.execution_in_progress = False
        st.session_state.execution_complete = True
    except Exception as e:
        st.session_state.execution_in_progress = False
        st.session_state.execution_error = str(e)

# Function to display the agent state
def display_agent_state():
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Plan & Progress", "🧠 Agent Thinking", "🛠️ Function Calls", "❌ Errors"])
    
    with tab1:
        st.subheader("Current Request")
        if 'current_input' in st.session_state:
            st.info(st.session_state.current_input)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Completed Steps")
            if 'past_steps' in st.session_state:
                for i, (step, result) in enumerate(st.session_state.past_steps):
                    with st.expander(f"Step {i+1}: {step[:50]}...", expanded=False):
                        st.write(f"**Action:** {step}")
                        st.write(f"**Result:** {result}")
            else:
                st.write("No steps completed yet")
        
        with col2:
            st.subheader("Upcoming Steps")
            if 'plan' in st.session_state and st.session_state.plan:
                for i, step in enumerate(st.session_state.plan):
                    st.write(f"{i+1}. {step}")
            else:
                st.write("No upcoming steps")
        
        if 'final_response' in st.session_state and st.session_state.final_response:
            st.subheader("Final Response")
            st.success(st.session_state.final_response)
    
    with tab2:
        st.subheader("Agent Thinking Log")
        if 'thinking_log' in st.session_state:
            for i, thought in enumerate(st.session_state.thinking_log):
                st.text(f"[{i+1}] {thought}")
        else:
            st.write("No thinking logged yet")
    
    with tab3:
        st.subheader("Function Calls")
        if 'function_log' in st.session_state and st.session_state.function_log:
            for i, func_call in enumerate(st.session_state.function_log):
                with st.expander(f"Call {i+1}: {func_call['function']}", expanded=False):
                    st.write(f"**Function:** {func_call['function']}")
                    st.write("**Parameters:**")
                    for param, value in func_call['parameters'].items():
                        st.write(f"- {param}: {value}")
                    st.write(f"**Result:** {func_call['result']}")
        else:
            st.write("No function calls yet")
    
    with tab4:
        st.subheader("Errors")
        if 'error_log' in st.session_state and st.session_state.error_log:
            for i, error in enumerate(st.session_state.error_log):
                st.error(f"Error {i+1}: {error}")
        else:
            st.write("No errors logged yet")
    
    # Show execution status
    if 'execution_in_progress' in st.session_state and st.session_state.execution_in_progress:
        st.info("Execution in progress...")
    elif 'execution_complete' in st.session_state and st.session_state.execution_complete:
        st.success("Execution complete!")
    elif 'execution_error' in st.session_state:
        st.error(f"Execution failed: {st.session_state.execution_error}")

if __name__ == "__main__":
    main()
