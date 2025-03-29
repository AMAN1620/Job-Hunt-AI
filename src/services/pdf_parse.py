from flask import Flask
from flask_cors import CORS
import pdfplumber
import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app) 
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# use pdf plumber and openai to fetch data
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_info_with_gpt(resume_text):
    prompt = f"""
    Extract the following details from the resume text:
    - Current Job Role
    - Location
    - Skills
    - Years of experience

    refer this as an example to format:
    {{
      "current_job_role": "Software Developer",
      "location": "New York, USA",
      "skills": ["Python", "Machine Learning", "React"],
      "years_of_experience": 5
    }}

    Resume text:
    {resume_text}
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", 
             "content": """You are an AI assistant that extracts structured data from resumes and returns only JSON output.  
                        Always respond in the following format without any additional text or explanations:  

                        {
                        "location": "New York, USA",
                        "skills": ["Python", "Machine Learning", "React"],
                        "years_of_experience": 5,
                        }

                        - If any field is missing from the resume, set its value to "N/A".  
                        - Calculate "years_of_experience" based on the work experience duration provided in the resume.  
                        - Ensure the JSON is properly formatted and valid.  
                        - Do not include any extra commentary, explanations, or formatting beyond the JSON structure."""}, 
            {"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)
