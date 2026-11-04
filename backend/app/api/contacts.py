from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.contact import TrustedContact
from app.schemas.contact import TrustedContactCreate, TrustedContactResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/contacts", tags=["Trusted Contacts"])

@router.get("/", response_model=List[TrustedContactResponse])
def get_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(TrustedContact).filter(TrustedContact.user_id == current_user.id).order_by(TrustedContact.is_primary.desc()).all()

@router.post("/", response_model=TrustedContactResponse, status_code=status.HTTP_201_CREATED)
def add_contact(
    contact_in: TrustedContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if contact_in.is_primary:
        # Demote existing primary contacts
        db.query(TrustedContact).filter(TrustedContact.user_id == current_user.id).update({"is_primary": False})

    contact = TrustedContact(
        user_id=current_user.id,
        contact_name=contact_in.contact_name.strip(),
        contact_phone=contact_in.contact_phone.strip(),
        contact_email=contact_in.contact_email,
        relationship=contact_in.relationship.strip(),
        is_primary=contact_in.is_primary
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(TrustedContact).filter(
        TrustedContact.id == contact_id,
        TrustedContact.user_id == current_user.id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")

    db.delete(contact)
    db.commit()
    return None

