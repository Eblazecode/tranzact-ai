from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.config import settings
from core.auth import verify_password, get_password_hash, create_access_token
from models.user import User
from .schemas import UserRegister, UserLogin, Token


def register_user(db: Session, user_data: UserRegister) -> Token:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name
        }
    )


def login_user(db: Session, login_data: UserLogin) -> Token:
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name
        }
    )
