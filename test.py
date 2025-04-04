from framework.cv_builder import CV_Builder
from framework.connectors.notion.connector import NotionConnection
from framework.bookkeepers.job_applications import JobApplicationManager
from framework.core.brains import get_model,Models
from framework.core.config_manager import master_cv_bullets, master_cv, settings

from dotenv import load_dotenv
import os

load_dotenv()

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
    
    
    
test_app()