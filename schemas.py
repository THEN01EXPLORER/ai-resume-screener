from pydantic import BaseModel , Field
from typing import List

class ExtractedResume(BaseModel):
    candidate_name: str = Field(description = "The full name of the candidate")
    technical_skills: List[str] = Field(description = "List of tools, languages, and Frameworks")
    total_experience_years: float = Field(description ="Total calculated years of professional experience")
    is_student: bool = Field(description = "True if currently enrolled in a degree program")

class JobDescription(BaseModel):
    title: str = Field(description="The job title")
    required_skills: List[str] = Field(description="Must-have technical skills")
    minimum_experience_years: float = Field(description="Minimum years of experience required")
    text_description: str = Field(description="The full paragraph description of the role")