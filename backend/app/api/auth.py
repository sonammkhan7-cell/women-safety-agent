from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse, UserProfileUpdate
)
from app.services.auth_service import (
    register_user, authenticate_user, get_current_user
)
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user_in)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials)
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Compatible with Swagger UI authorize button
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    user = authenticate_user(db, login_data)
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_data.name:
        current_user.name = profile_data.name
    if profile_data.phone_number is not None:
        current_user.phone_number = profile_data.phone_number
    if profile_data.emergency_note is not None:
        current_user.emergency_note = profile_data.emergency_note
    db.commit()
    db.refresh(current_user)
    return current_user

