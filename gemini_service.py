import os
import re
import time
from google import genai
from dotenv import load_dotenv
from schemas import ExtractedResume

# Load the API key from your .env file
load_dotenv()


def extract_resume_data(resume_text: str) -> ExtractedResume | None:
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are a technical recruiter. Extract the requested information from the resume text below. 
    Calculate the total years of professional experience carefully. If they are in college, is_student is true.
    
    Resume Text:
    {resume_text}
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': ExtractedResume,
                    'temperature': 0.1
                }
            )
            return response.parsed
        except Exception as e:
            err_str = str(e)
            # Only retry on 429 rate limit errors
            if '429' in err_str and attempt < max_retries - 1:
                # Try to parse the suggested retry delay from the error message
                match = re.search(r'retry in (\d+)', err_str, re.IGNORECASE)
                wait_sec = int(match.group(1)) if match else 30
                print(f"---> [RATE LIMIT] Quota hit. Retrying in {wait_sec}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_sec + 2)  # small buffer
            else:
                raise  # re-raise for non-429 errors or final attempt
    return None  # Should never be reached, but makes the implicit return explicit