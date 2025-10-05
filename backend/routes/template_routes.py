from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from models.cv import CVTemplate
from services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])

# Initialize template service
template_service = TemplateService()

@router.get("/", response_model=List[CVTemplate])
async def get_all_templates(category: Optional[str] = None):
    """Get all CV templates, optionally filtered by category"""
    
    if category:
        templates = template_service.get_templates_by_category(category)
    else:
        templates = template_service.get_all_templates()
    
    return templates

@router.get("/categories")
async def get_template_categories():
    """Get all available template categories"""
    
    categories = set()
    for template in template_service.get_all_templates():
        categories.add(template.category)
    
    return {"categories": sorted(list(categories))}

@router.get("/{template_id}", response_model=CVTemplate)
async def get_template(template_id: str):
    """Get a specific template by ID"""
    
    template = template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template

@router.get("/preview/{template_id}")
async def get_template_preview(template_id: str):
    """Get template preview data"""
    
    template = template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Return sample data for preview
    sample_data = {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1 (555) 123-4567",
            "location": "New York, NY",
            "linkedin": "linkedin.com/in/johndoe",
            "summary": "Experienced professional with expertise in technology and innovation."
        },
        "experience": {
            "experiences": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "start_date": "2020",
                    "end_date": "Present",
                    "description": "Led development of innovative software solutions and managed cross-functional teams."
                }
            ]
        },
        "education": {
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "University of Technology",
                    "start_date": "2016",
                    "end_date": "2020"
                }
            ]
        },
        "skills": {
            "skills": ["JavaScript", "Python", "React", "Node.js", "AWS"]
        }
    }
    
    return {
        "template": template,
        "sample_data": sample_data
    }