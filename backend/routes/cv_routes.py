from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from models.cv import CVData, CVCreate, CVUpdate, CVResponse
from models.user import User
from auth.auth import get_current_user_dependency
from database import get_database
import os
from datetime import datetime

router = APIRouter(prefix="/cv", tags=["cv"])

@router.post("/", response_model=CVResponse)
async def create_cv(
    cv_data: CVCreate,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create a new CV"""
    
    # Create CV object
    cv = CVData(
        user_id=current_user.id,
        title=cv_data.title,
        template_id=cv_data.template_id,
        sections=cv_data.sections
    )
    
    # Save to database
    cv_dict = cv.dict()
    result = await db.cvs.insert_one(cv_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create CV"
        )
    
    return CVResponse(**cv.dict())

@router.get("/", response_model=List[CVResponse])
async def get_user_cvs(
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get all CVs for the current user"""
    
    cvs = await db.cvs.find({"user_id": current_user.id}).to_list(1000)
    return [CVResponse(**cv) for cv in cvs]

@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get a specific CV"""
    
    cv = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    return CVResponse(**cv)

@router.put("/{cv_id}", response_model=CVResponse)
async def update_cv(
    cv_id: str,
    cv_update: CVUpdate,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Update a CV"""
    
    # Check if CV exists and belongs to user
    existing_cv = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not existing_cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    # Update fields
    update_data = {}
    if cv_update.title is not None:
        update_data["title"] = cv_update.title
    if cv_update.template_id is not None:
        update_data["template_id"] = cv_update.template_id
    if cv_update.sections is not None:
        update_data["sections"] = [section.dict() for section in cv_update.sections]
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update in database
    result = await db.cvs.update_one(
        {"id": cv_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update CV"
        )
    
    # Return updated CV
    updated_cv = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    return CVResponse(**updated_cv)

@router.delete("/{cv_id}")
async def delete_cv(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Delete a CV"""
    
    result = await db.cvs.delete_one({"id": cv_id, "user_id": current_user.id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    return {"message": "CV deleted successfully"}

@router.post("/{cv_id}/duplicate", response_model=CVResponse)
async def duplicate_cv(
    cv_id: str,
    db: AsyncIOMotorClient = Depends(get_database),
    current_user: User = Depends(get_current_user_dependency)
):
    """Duplicate a CV"""
    
    # Get original CV
    original_cv = await db.cvs.find_one({"id": cv_id, "user_id": current_user.id})
    if not original_cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found"
        )
    
    # Create new CV
    new_cv = CVData(
        user_id=current_user.id,
        title=f"{original_cv['title']} (Copy)",
        template_id=original_cv["template_id"],
        sections=original_cv["sections"]
    )
    
    # Save to database
    result = await db.cvs.insert_one(new_cv.dict())
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate CV"
        )
    
    return CVResponse(**new_cv.dict())