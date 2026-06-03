from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import get_current_user
from core.database import get_db
from models.user import User
from .schemas import UserRegister, UserLogin, UserResponse
from .service import register_user, login_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(db, user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
