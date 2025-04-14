from framework.cv_builder import CV_Builder
from framework.connectors.notion.connector import NotionConnection
from framework.bookkeepers.job_applications import JobApplicationManager
from framework.core.brains import get_model,Models
from framework.core.config_manager import master_cv_bullets, master_cv, settings
from agent_trials3.base_agent import base_agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.groq import GroqModel
import asyncio


from dotenv import load_dotenv
import os

load_dotenv()


def llm_ollama(name:str)->OpenAIModel:
    return OpenAIModel(
    model_name=name, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
) 




def test_app():
    llm = get_model(Models.CLAUDE_SONNET)
    cv= CV_Builder(llm=llm)
    user_input=" "
    jd=""
    with open('config/jd_temp.txt', 'r') as file:
        jd = file.read()
    response= cv.build_cv_components( jd=jd,user_input=user_input
    )

    print ("****************************************************")
    print (response)
    
    
def test_app_tracking():
    print ("creating a notion connection")
    notion= NotionConnection(os.getenv("NOTION_INTEGRATION_SECRET"))
    application_database_id= settings.get('databases').get("applications")
    job_manager = JobApplicationManager(notion, database_id=application_database_id)
    
    job_manager.add_application(
    company="Acme Inc",
    role="Software Developer",
    url="https://acme.com/careers/123",
    location="Remote",
    contact_person="Jane Recruiter",
    job_description="Full-stack developer position...",
    confidence="Medium",
    referral="Yes"
    )
    
    
    
async def test_app2(input_text):
    agent = base_agent(
        llm_think=OpenAIModel("gpt-4o-mini"),
        llm_interact=llm_ollama("qwen2.5-coder:14b"),
        llm_do=OpenAIModel("gpt-4o-mini")
    )
    
    # Get the app
    app = agent.get_app()
    
    # Run the agent
    inputs = {"input": input_text}
    config = {}
    
    try:
        async for event in app.astream(inputs, config=config):
            for k, v in event.items():
                if k != "__end__":
                    agent.display.thinking(f"Event: {k} = {v}")
    except Exception as e:
        agent.display.error(f"Error running agent: {str(e)}")
    
    # Keep the display running until user closes it
    # In a real implementation, you might want to provide a way to cleanly exit
    try:
        while True:
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        agent.display.stop()
    
    
    
if __name__ == "__main__":
    asyncio.run(test_app2("tell me about weather in London and Paris"))