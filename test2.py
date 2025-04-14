import streamlit as st
import os
import asyncio

# Import your modules
from agent_trials3.base_agent import base_agent
from agent_trials3.displays.streamlit_based import StreamlitAgentUI

# Import model definitions (or use appropriate imports for your project)
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

# IMPORTANT: This must be the first Streamlit command
st.set_page_config(page_title="Agent Trials Platform", layout="wide")

# Set up API keys (better to use environment variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-groq-api-key")

def get_model(model_name):
    """Get the appropriate model based on the selected name"""
    if model_name == "OpenAI GPT-4o":
        return OpenAIModel(model="gpt-4o")
    elif model_name == "OpenAI GPT-4o-mini":
        return OpenAIModel( model="GPT-4o-mini")
    elif model_name == "Groq llama4":
        return GroqModel( model="meta-llama/llama-4-scout-17b-16e-instruct")
    else:
        return OpenAIModel( model="GPT-4o-mini")

# Initialize the Streamlit UI if not already in session state
if 'ui' not in st.session_state:
    st.session_state.ui = StreamlitAgentUI()

# Sidebar for agent configuration
with st.sidebar:
    st.title("🤖 Agent Configuration")
    
    # Model selection dropdowns
    think_model_name = st.selectbox(
        "Thinking Model",
        ["OpenAI GPT-4o", "GPT-4o-mini", "Groq llama4"],
        index=0
    )
    
    do_model_name = st.selectbox(
        "Doing Model",
        ["OpenAI GPT-4o", "GPT-4o-mini", "Groq llama4"],
        index=2
    )
    
    interact_model_name = st.selectbox(
        "Interaction Model",
        ["OpenAI GPT-4o", "GPT-4o-mini", "Groq llama4"],
        index=2
    )
    
    # Agent initialization button
    if st.button("Initialize Agent"):
        with st.spinner("Initializing agent..."):
            try:
                # Get the model instances
                llm_think = get_model(think_model_name)
                llm_do = get_model(do_model_name)
                llm_interact = get_model(interact_model_name)
                
                # Create the base agent
                agent = base_agent(
                    llm_think=llm_think,
                    llm_do=llm_do,
                    llm_interact=llm_interact
                )
                
                # Connect the agent to our UI
                st.session_state.ui.set_agent(agent)
                
                st.success("Agent initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize agent: {str(e)}")

# Run the UI with the connected agent
st.session_state.ui.run_app()