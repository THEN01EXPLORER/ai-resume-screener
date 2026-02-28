from fastapi import FastAPI, UploadFile, File, HTTPException
from pdf_parser import validate_pdf_magic_bytes, clean_extracted_text
from gemini_service import extract_resume_data
from embedding_service import add_resume_to_db, query_resumes, get_resume_count
from typing import Annotated, List
from schemas import JobDescription
from ranking_service import calculate_skill_match, calculate_final_score
import pdfplumber
import io

app = FastAPI(title="Resume Screener Core")

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_content = await file.read()
    
    if not validate_pdf_magic_bytes(file_content):
        raise HTTPException(status_code=400, detail="Security alert: Invalid file signature.")
    
    extracted_text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
        
    cleaned_text = clean_extracted_text(extracted_text)

    # Guard: reject PDFs with too little text (scanned images, certificates, etc.)
    if len(cleaned_text.strip()) < 100:
        raise HTTPException(
            status_code=422,
            detail=(
                "This PDF appears to be a scanned image or certificate and could not be read as a resume. "
                "Please upload a text-based resume PDF."
            )
        )
    
    try:
        structured_data = extract_resume_data(cleaned_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction Failed: {str(e)}")

    # Guard: Gemini may return None if the document is not a resume
    if structured_data is None:
        raise HTTPException(
            status_code=422,
            detail="AI could not extract resume data from this file. Please make sure it is a proper resume."
        )
        
    # --- VECTOR DB STEP ---
    skills_list = structured_data.technical_skills
    
    try:
        print(f"\n---> [SYSTEM] Attempting to save {file.filename} to ChromaDB...")
        add_resume_to_db(
            filename=file.filename,
            text=cleaned_text,
            skills=skills_list,
            experience=structured_data.total_experience_years 
        )
        print("---> [SYSTEM] Successfully saved to Vector Memory!\n")
    except Exception as e:
        print(f"\n---> [CRITICAL ERROR] Failed to save to DB: {e}\n")
        
    return {
        "filename": file.filename,
        "status": "Success",
        "extracted_data": structured_data.model_dump() 
    }


@app.post("/upload-bulk/")
async def upload_bulk_resumes(files: Annotated[List[UploadFile], File(description="Select multiple PDFs")]):
    """
    Ingests multiple PDF resumes in a single API call.
    """
    processed_files = []
    failed_files = []

    for file in files:
        try:
            # 1. Validation
            if not file.filename.lower().endswith(".pdf"):
                failed_files.append({"filename": file.filename, "reason": "Not a PDF"})
                continue # Skip to the next file
            
            file_content = await file.read()
            
            if not validate_pdf_magic_bytes(file_content):
                failed_files.append({"filename": file.filename, "reason": "Invalid signature"})
                continue
            
            # 2. Parsing
            extracted_text = ""
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
                        
            cleaned_text = clean_extracted_text(extracted_text)
            
            # Guard: reject PDFs with too little text (scanned images, certificates, etc.)
            if len(cleaned_text.strip()) < 100:
                failed_files.append({"filename": file.filename, "reason": "Appears to be a scanned image — no readable text found."})
                continue
                
            # 3. AI Extraction
            structured_data = extract_resume_data(cleaned_text)
            
            # Guard: Gemini may return None if the document is not a resume
            if structured_data is None:
                failed_files.append({"filename": file.filename, "reason": "AI could not extract resume data. Please ensure it is a valid resume."})
                continue

            skills_list = structured_data.technical_skills
            
            # 4. Vector DB Storage
            print(f"---> [SYSTEM] Saving {file.filename} to Vector Memory...")
            add_resume_to_db(
                filename=file.filename,
                text=cleaned_text,
                skills=skills_list,
                experience=structured_data.total_experience_years
            )
            
            processed_files.append(file.filename)
            
        except Exception as e:
            # If AI parsing or DB storage fails, log it and keep moving
            failed_files.append({"filename": file.filename, "reason": str(e)})

    return {
        "status": "Batch Complete",
        "total_processed": len(processed_files),
        "total_failed": len(failed_files),
        "successful_uploads": processed_files,
        "failed_uploads": failed_files
    }   

@app.post("/match/")
async def match_resumes(job: JobDescription): 
    try:
        # Dynamically get total count so we rank ALL resumes, not just top 5
        total_in_db = get_resume_count()
        
        if total_in_db == 0:
            return {"message": "No resumes found in the database. Please upload some first."}
        
        # Ask ChromaDB for every resume in the database
        db_results = query_resumes(query_text=job.text_description, n_results=total_in_db)
            
        ranked_candidates = []
        
        # 2. Loop through every single candidate ChromaDB returned
        # db_results['ids'][0] contains the list of filenames it found
        for i in range(len(db_results['ids'][0])):
            candidate_id = db_results['ids'][0][i]
            distance = db_results['distances'][0][i]
            metadata = db_results['metadatas'][0][i]
            
            # Extract real data for this specific candidate
            real_skills = [s.strip() for s in metadata['skills'].split(',')]
            real_experience = metadata.get('experience', 0.0) 
            
            # Run the Math for this candidate
            skill_ratio = calculate_skill_match(real_skills, job.required_skills)
            score_report = calculate_final_score(
                vector_distance=distance,
                skill_match_ratio=skill_ratio,
                resume_exp=real_experience,
                required_exp=job.minimum_experience_years
            )
            
            # Package their results and add them to our master list
            ranked_candidates.append({
                "candidate_id": candidate_id,
                "scoring_report": score_report
            })
            
        # 3. The Sorting Algorithm
        # Sort the entire list by 'final_percentage' from highest to lowest
        ranked_candidates.sort(key=lambda x: x["scoring_report"]["final_percentage"], reverse=True)
        
        return {
            "job_title": job.title,
            "total_candidates_scored": len(ranked_candidates),
            "rankings": ranked_candidates # Returns the sorted array
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")