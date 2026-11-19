from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.verification import (
    VerificationSubmit, VerificationReview, VerificationResponse,
    AdminVerificationResponse
)
from app.services.auth_service import get_current_user, get_current_admin
from app.services.verification_service import (
    submit_verification, get_user_verification, list_pending_verifications, review_verification
)

router = APIRouter(prefix="/verification", tags=["Eligibility Verification"])

@router.post("/submit", response_model=VerificationResponse)
def submit(
    data: VerificationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return submit_verification(db, current_user, data)

@router.get("/status", response_model=VerificationResponse)
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verif = get_user_verification(db, current_user.id)
    if not verif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification submission found for this user."
        )
    return verif

@router.get("/admin/all", response_model=List[AdminVerificationResponse])
def get_all_for_admin(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return [
        {
            **VerificationResponse.model_validate(verification).model_dump(),
            "user_name": verification.user.name,
            "user_email": verification.user.email,
        }
        for verification in list_pending_verifications(db)
    ]

@router.post("/admin/review/{verification_id}", response_model=VerificationResponse)
def review(
    verification_id: int,
    review_data: VerificationReview,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return review_verification(db, verification_id, review_data, admin)

