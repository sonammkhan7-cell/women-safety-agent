from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, VerificationStatus, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def register_user(db: Session, user_in: UserRegister) -> User:
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # Check if first user in system, make admin for easy review in MVP
    is_first = db.query(User).count() == 0
    role = UserRole.ADMIN if is_first else UserRole.USER

    user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hash_password(user_in.password),
        phone_number=user_in.phone_number,
        emergency_note=user_in.emergency_note,
        is_email_verified=True,  # Initially marked true or via verification link
        verification_status=VerificationStatus.PENDING,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, credentials: UserLogin) -> User:
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user_id = payload.get("sub")
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except (ValueError, TypeError):
        user = None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.verification_status != VerificationStatus.VERIFIED and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Eligibility verification required. Only verified women can access companion matching."
        )
    return current_user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    return current_user

