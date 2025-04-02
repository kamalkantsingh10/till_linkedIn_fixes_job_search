from framework.core.config_manager import master_cv_bullets, master_cv, settings

class CV_Builder:
    
    def __init__(self, llm):
        self.llm=llm
    
    def analyse_job_description(self, jd:str, user_input:str)->str:
        
        messages = [
        (
        "system",
        """You are a senior leader manager reviewing CVs for a leadership position. Please provide analysis that a CV writer will use to write a cv that is best fit for this role.

        INSTRUCTIONS Analyze the job description to identify the top 6 skills/abilities that will maximize interview chances. Provide instructions for CV writers on what should be covered for bullet points. Prioritize skills that appear repeatedly, are mentioned early, or are emphasized in the JD. INPUT 

        OUTPUT FORMAT Provide these three sections
        Top 6 Skills to Highlight
        [SKILL 1] - [Brief explanation of why this is critical based on the JD]
        [SKILL 2] - [Brief explanation of why this is critical based on the JD]
        [SKILL 3] - [Brief explanation of why this is critical based on the JD] 
        [SKILL 4] - [Brief explanation of why this is critical based on the JD] 
        [SKILL 5] - [Brief explanation of why this is critical based on the JD]
        [SKILL 6] - [Brief explanation of why this is critical based on the JD]

        Key Terminology
        List 5-10 specific terms, phrases, or buzzwords from the JD that should be incorporated in your application

        instructions for the CV writer
        Look for skills mentioned in the "Requirements" or "Qualifications" sections Identify any skills mentioned in the first paragraph or job summary Note any skills mentioned multiple times throughout the JD Prioritize technical skills and specialized knowledge Include both hard skills (technical abilities) and soft skills (leadership, communication) Consider skills listed as "required" over those listed as "preferred" """
            ),
            ("human", f"""JD here:-----
             {jd}


            also consider directions from user:---
            {user_input}
            """),
        ]
        
        ai_msg = self.llm.invoke(messages)
        return ai_msg.content
        
    
    def generate_tagline_skills(self, jd:str, user_input:str)-> str:
        messages = [
        (
        "system",
        """You are a professional CV/resume writer specializing in leadership positions.

            Based on the job description I provide and my current CV:

            a. Create a compelling professional tagline (maximum 15 words) that I can place below my name in my CV header. This should highlight my key value proposition for this leadership role. Mention 15+ years of experience

            b. Generate a skills section organized into three categories (including one for technical skills), with 6 skills per category. For each skill:
            i. Ensure all essential skills from the job description are included
            ii. Keep each skill description between 3-6 words
            iii. Balance the requirements in the job description with my demonstrated experience
            iv. Prioritize leadership competencies relevant to the position

            Format the skills in a clean, scannable layout that I can easily transfer to my CV.

        """
            ),
            ("human", f"""JD here:-----
             {jd}

            CV here:
            {master_cv}

            also consider directions from user:---
            {user_input}
            """),
        ]
        
        ai_msg = self.llm.invoke(messages)
        return ai_msg.content
    
    def build_bullets(self,jd_analysis:str, user_input:str)-> str:
        
        bullets=""
        
        for role_info in master_cv_bullets.get('bullets_to_update'):
            
            role_title = role_info.get('role', 'Unnamed Role')
            requested_bullets = role_info.get('number_bullets', 3)
            text_content = role_info.get('text', '')
            bullet=role_title
            print(f"\n{'='*50}")
            print(f"Role: {role_title}")
            print(f"Number of bullets requested: {requested_bullets}")
            
            # code tp call LLM and create compatible bullet points
            messages = [
            (
            "system",
            """You are a professional CV/resume writer specializing in leadership positions.

                Create concise CV bullet points as requested. try to stay within 16 words for each bullet
            
                Create bullet points that:
                *follow the analysis of JD provided
                * Include only the most impressive metrics
                * Focus on direct business impact
                * Use keywords relevant to the role
                * all bullets collectively should support the CV
                * it is important that you stay truthful 
                
                BULLET POINT STRUCTURE
                    [Action Verb] [key achievement] [most impressive metric]
                    
                EXAMPLES
                    -Spearheaded transformation of 23+ innovation centers with 241+ people and $150M -budget.  Developed processes across 19+ product roles; delivered first SaaS release.
                    -Improved security cloud business by triple digits; generated $22.5M+ annually.
                    -Monetized data via IoT offerings and ML analytics with 45+ counterparts.

            """
                ),
            ("human", f"""JD analyis here:-----
             {jd_analysis}

            section text here:
            {text_content}
            
            number of bullets needed: {requested_bullets}

            also consider directions from user:---
            {user_input}
            """),
            ]
            
            ai_msg = self.llm.invoke(messages)
            bullet= bullet+ "\n" + ai_msg.content
            bullets= bullets+ "\n\n\n" +bullet
        
        return bullets
            
    
    def build_cv_components(self, jd:str, user_input:str)-> str:
        #step 1 - Analyse JD
        print("analysing JD")
        jd_analysis= self.analyse_job_description(jd=jd, user_input=user_input)
               
        print(f"JD analysis done \n {jd_analysis}")
        #step 2 - get bullets
        bullets= self.build_bullets(jd_analysis=jd_analysis, user_input=user_input)
        print(f"Bullets created \n {bullets}")
        #step 3 - get tagline and skills
        tagline_skills= self.generate_tagline_skills(jd=jd, user_input=user_input)
        print(f"taglines generated: \n {tagline_skills}")
        return f"""
        ************************************************************************************
        {bullets}
        -------------------
        {tagline_skills}
        
        ----------------------------------
        jd analysis
        {jd_analysis}
        """
        
    
  
    
    
    
    
        