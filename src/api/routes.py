from flask import request, jsonify
from fastapi import APIRouter, Depends, HTTPException, Body, Request, HTTPException
from services.job_search import JobHuntingAgent
from services.pdf_parse import extract_text_from_pdf
from services.pdf_parse import extract_info_with_gpt
from models.job_search_model import JobRequirements
from dotenv import load_dotenv
import os
from langfuse.decorators import observe
import uuid
from redis_module.records import ResponseModel
from redis_module.cache import Cache
from redis_module.config import Redis
import logging

load_dotenv()

router = APIRouter()

firecrawl_api_key = os.getenv("FIRE_CRAWL_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model_id = os.getenv("MODEL")

# os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
# os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")

# instance created for the JobSchema
job_agent = JobHuntingAgent(firecrawl_api_key=firecrawl_api_key,openai_api_key=openai_api_key,model_id=model_id)
redis_client = Redis()

@router.get("/health_check/")
def test_health():
    return {"message": "App is runnung!!"}


@router.post("/generate_token/")
async def token_generator(request: Request):
    try:
        token = str(uuid.uuid4())
        logging.info(f"token generated [{token}]")

        response_model = ResponseModel(
            token=str(token),
            msg="Hello there",
        )

        # creating redis connection
        await redis_client.create_connection()
        cache = Cache(redis_client)

        # saving token to cache
        await cache.add_response_to_cache(token=str(token),message_data=response_model.model_dump())
        return {"token": token}
    
    except:
        raise HTTPException(status_code=400, detail={
            "Response": "Something went wrong in token generation"})

@router.post("/pdf_data_extract")
async def extract_pdf_data():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]

    extracted_text = extract_text_from_pdf(file)
    extracted_info = extract_info_with_gpt(extracted_text)

    return jsonify(extracted_info)

@router.post("/find_jobs/")
async def find_matching_jobs(token:str, job_requirement: JobRequirements = Body()):
    try:
        logging.info(f"token is {token}")
        job_title = job_requirement.job_title
        location = job_requirement.location
        experience_years = job_requirement.experience
        skills = job_requirement.skills

        response = job_agent.find_jobs(
            job_title=job_title,
            location=location,
            experience_years=experience_years,
            skills=skills
        )
        print(response)
        if response:
            # token = "9cfc387a-3d0f-433a-a702-25d12eb2c575"
            response_model = ResponseModel(
                    token=str(token),
                    msg=str(response),
            )
            await redis_client.create_connection()
            logging.info(f"Connection created successfully")
            cache = Cache(redis_client)
            await cache.add_response_to_cache(token=str(token),message_data=response_model.model_dump())
            logging.info(f"token saved to cahche successfully")
            pass
        if not response:
            raise HTTPException(status_code=404, detail="No jobs found matching the criteria")
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")