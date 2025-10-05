from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class CVSection(BaseModel):
    type: str  # personal_info, experience, education, skills, projects, etc.
    title: str
    content: Dict[str, Any]
    order: int = 0
    is_visible: bool = True

class CVTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str  # professional, creative, modern, classic
    preview_url: Optional[str] = None
    is_premium: bool = False
    styles: Dict[str, Any] = {}  # CSS styles, colors, fonts
    layout: str = "single-column"  # single-column, two-column, etc.
    
class CVData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    template_id: str
    sections: List[CVSection] = []
    ats_score: Optional[int] = None
    ats_suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    
class CVCreate(BaseModel):
    title: str
    template_id: str
    sections: List[CVSection] = []
    
class CVUpdate(BaseModel):
    title: Optional[str] = None
    template_id: Optional[str] = None
    sections: Optional[List[CVSection]] = None
    
class CVResponse(BaseModel):
    id: str
    title: str
    template_id: str
    sections: List[CVSection]
    ats_score: Optional[int]
    ats_suggestions: List[str]
    created_at: datetime
    updated_at: datetime