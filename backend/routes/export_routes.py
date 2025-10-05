from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response
from motor.motor_asyncio import AsyncIOMotorClient
from models.cv import CVData
from models.user import User
from auth.auth import get_current_user_dependency
from services.export_service import ExportService
from services.template_service import TemplateService
from database import get_database
import os

router = APIRouter(prefix="/export", tags=["export"])

# Initialize services
export_service = ExportService()
template_service = TemplateService()

@router.get("/{cv_id}/pdf")
async def export_cv_to_pdf(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Export CV to PDF format"""
    
    # Get CV data
    cv_data = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not cv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    try:
        # Convert to CVData object
        cv = CVData(**cv_data)
        
        # Get template styles
        template = template_service.get_template_by_id(cv.template_id)
        template_styles = template.styles if template else {}
        
        # Generate PDF
        pdf_content = await export_service.export_to_pdf(cv, template_styles)
        
        # Return PDF as response
        filename = f"{cv.title.replace(' ', '_')}.pdf"
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF export failed: {str(e)}"
        )

@router.get("/{cv_id}/html")
async def export_cv_to_html(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Export CV to HTML format"""
    
    # Get CV data
    cv_data = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not cv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    try:
        # Convert to CVData object
        cv = CVData(**cv_data)
        
        # Get template styles
        template = template_service.get_template_by_id(cv.template_id)
        template_styles = template.styles if template else {}
        
        # Generate HTML
        html_content = await export_service.export_to_html(cv, template_styles)
        
        # Return HTML as response
        filename = f"{cv.title.replace(' ', '_')}.html"
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTML export failed: {str(e)}"
        )

@router.get("/{cv_id}/word")
async def export_cv_to_word(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Export CV to Word format (HTML-based)"""
    
    # Get CV data
    cv_data = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not cv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    try:
        # Convert to CVData object
        cv = CVData(**cv_data)
        
        # Get template styles
        template = template_service.get_template_by_id(cv.template_id)
        template_styles = template.styles if template else {}
        
        # Generate Word-compatible HTML
        word_html = await export_service.export_to_word_html(cv, template_styles)
        
        # Return Word document
        filename = f"{cv.title.replace(' ', '_')}.doc"
        return Response(
            content=word_html,
            media_type="application/msword",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Word export failed: {str(e)}"
        )

@router.get("/{cv_id}/json")
async def export_cv_to_json(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Export CV to JSON format"""
    
    # Get CV data
    cv_data = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not cv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    try:
        # Return JSON data
        filename = f"{cv_data['title'].replace(' ', '_')}.json"
        
        # Remove MongoDB ObjectId and other non-serializable fields
        clean_cv_data = {k: v for k, v in cv_data.items() if k != '_id'}
        
        return Response(
            content=str(clean_cv_data).replace("'", '"'),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON export failed: {str(e)}"
        )