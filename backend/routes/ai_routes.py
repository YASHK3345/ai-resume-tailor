from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.ai import AIContentRequest, AIContentResponse, ATSAnalysisRequest, ATSAnalysisResponse
from models.user import User
from auth.auth import get_current_user_dependency
from services.ai_service import AIService
from database import get_database
import os

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize AI service
ai_service = AIService()

@router.post("/optimize-content", response_model=AIContentResponse)
async def optimize_content(
    request: AIContentRequest,
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Optimize CV content using AI"""
    
    try:
        # Check user subscription for AI features
        if current_user.subscription_tier == "free":
            # Limit AI requests for free users (could be implemented with rate limiting)
            pass
        
        # Optimize content using AI
        result = await ai_service.optimize_content(request)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI optimization failed: {str(e)}"
        )

@router.post("/analyze-ats", response_model=ATSAnalysisResponse)
async def analyze_ats(
    request: ATSAnalysisRequest,
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Analyze CV for ATS compatibility"""
    
    try:
        # Analyze ATS compatibility
        result = await ai_service.analyze_ats_score(request)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS analysis failed: {str(e)}"
        )

@router.post("/suggestions")
async def get_ai_suggestions(
    section_type: str,
    job_title: str = None,
    current_user: User = Depends(lambda: get_current_user(db=get_database()))
):
    """Get AI suggestions for CV sections"""
    
    try:
        # Create basic content request for suggestions
        request = AIContentRequest(
            section_type=section_type,
            job_title=job_title or "General",
            existing_content="",
            target_keywords=[],
            tone="professional"
        )
        
        # Get suggestions
        result = await ai_service.optimize_content(request)
        
        return {
            "suggestions": result.suggestions,
            "sample_content": result.optimized_content
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI suggestions: {str(e)}"
        )