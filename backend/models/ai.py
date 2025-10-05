from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AIContentRequest(BaseModel):
    section_type: str  # experience, skills, summary, etc.
    job_title: str
    company: Optional[str] = None
    existing_content: str
    target_keywords: List[str] = []
    tone: str = "professional"  # professional, creative, casual
    
class AIContentResponse(BaseModel):
    optimized_content: str
    suggestions: List[str]
    keywords_used: List[str]
    ats_score: int
    
class ATSAnalysisRequest(BaseModel):
    cv_content: str
    job_description: Optional[str] = None
    
class ATSAnalysisResponse(BaseModel):
    overall_score: int
    section_scores: Dict[str, int]
    suggestions: List[str]
    missing_keywords: List[str]
    keyword_density: Dict[str, float]