def calculate_skill_match(resume_skills: list, required_skills: list) -> float:
    """Calculates the percentage of required skills found in the resume."""
    if not required_skills:
        return 1.0 # If they didn't ask for any skills, it's a 100% match
        
    
    r_skills = [s.lower() for s in resume_skills]
    req_skills = [s.lower() for s in required_skills]
    

    matches = sum(1 for skill in req_skills if skill in r_skills)
    return matches / len(req_skills)

def calculate_final_score(
    vector_distance: float, 
    skill_match_ratio: float, 
    resume_exp: float, 
    required_exp: float
) -> dict:
    """
    The Hybrid Scoring Algorithm.
    ChromaDB returns distance (smaller is better). We convert it to similarity (higher is better).
    """
    
    semantic_similarity = max(0.0, 1.0 - (vector_distance / 2.0))
    
  
    exp_score = 1.0 if resume_exp >= required_exp else 0.5 # 50% penalty if under-experienced
    final_score = (semantic_similarity * 0.40) + (skill_match_ratio * 0.40) + (exp_score * 0.20)
    
    return {
        "final_percentage": round(final_score * 100, 2),
        "semantic_score": round(semantic_similarity * 100, 2),
        "skill_match_score": round(skill_match_ratio * 100, 2),
        "experience_passed": resume_exp >= required_exp
    }