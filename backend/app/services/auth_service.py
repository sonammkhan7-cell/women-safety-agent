import logging
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User, VerificationStatus, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def register_user(db: Session, user_in: UserRegister) -> User:
    email_clean = user_in.email.lower().strip()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in instead."
        )
    
    user = User(
        name=user_in.name.strip(),
        email=email_clean,
        password_hash=hash_password(user_in.password),
        phone_number=user_in.phone_number,
        emergency_note=user_in.emergency_note,
        is_email_verified=False,
        verification_status=VerificationStatus.PENDING,
        role=UserRole.USER
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as ie:
        db.rollback()
        logger.warning(f"Integrity error during registration for {email_clean}: {ie}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in instead."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected database error during registration for {email_clean}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register account due to a database error. Please try again."
        )

def promote_user_to_admin(db: Session, email: str) -> User:
    email_clean = email.strip().lower()
    if not email_clean:
        raise ValueError("An account email is required.")

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise ValueError("No registered account exists for that email.")

    if user.role != UserRole.ADMIN:
        user.role = UserRole.ADMIN
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(user)

    return user

def authenticate_user(db: Session, credentials: UserLogin) -> User:
    email_clean = credentials.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please verify your credentials."
        )
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please verify your credentials."
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

