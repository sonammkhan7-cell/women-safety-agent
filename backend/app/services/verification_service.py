from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, VerificationStatus
from app.models.verification import Verification, DocumentType
from app.schemas.verification import VerificationSubmit, VerificationReview

def submit_verification(db: Session, user: User, data: VerificationSubmit) -> Verification:
    # Check if there is already an active pending submission
    pending = db.query(Verification).filter(
        Verification.user_id == user.id,
        Verification.status == VerificationStatus.PENDING
    ).first()
    
    ref = f"VERIF-{uuid.uuid4().hex[:8].upper()}"
    
    if pending:
        # Update existing pending
        pending.document_type = data.document_type
        pending.masked_identifier = data.masked_identifier
        pending.submission_notes = data.submission_notes
        pending.verification_reference = ref
        db.commit()
        db.refresh(pending)
        return pending

    verification = Verification(
        user_id=user.id,
        status=VerificationStatus.PENDING,
        document_type=data.document_type,
        masked_identifier=data.masked_identifier,
        submission_notes=data.submission_notes,
        verification_reference=ref
    )
    user.verification_status = VerificationStatus.PENDING
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification

def get_user_verification(db: Session, user_id: int) -> Optional[Verification]:
    return db.query(Verification).filter(Verification.user_id == user_id).order_by(Verification.created_at.desc()).first()

def list_pending_verifications(db: Session) -> List[Verification]:
    return db.query(Verification).order_by(Verification.created_at.desc()).all()

def review_verification(db: Session, verification_id: int, review_data: VerificationReview, reviewer: User) -> Verification:
    verification = db.query(Verification).filter(Verification.id == verification_id).first()
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification record not found."
        )
    
    verification.status = review_data.status
    verification.reviewer_notes = review_data.reviewer_notes
    verification.reviewed_at = datetime.now(timezone.utc)
    verification.reviewer_id = reviewer.id

    # Update associated user's verification status
    target_user = db.query(User).filter(User.id == verification.user_id).first()
    if target_user:
        target_user.verification_status = review_data.status
    
    db.commit()
    db.refresh(verification)
    return verification

