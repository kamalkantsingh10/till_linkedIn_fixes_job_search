from framework.cv_builder import CV_Builder
from framework.core.brains import get_model,Models
from dotenv import load_dotenv
load_dotenv()

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