from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.database.base import get_db
from app.database.models.identity import UserRole
from app.database.repositories.user_repository import create_user, get_user_by_email
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        email = user.email.strip().lower()
        if get_user_by_email(db, email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah terdaftar")

        password_hash = hash_password(user.password)
        created_user = create_user(db, email=email, password_hash=password_hash, role=UserRole.TRADER, status="ACTIVE")

        return {
            "success": True,
            "message": "User registered",
            "data": {"user_id": str(created_user.id)},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}") from e


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        email = form_data.username.strip().lower()
        db_user = get_user_by_email(db, email)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email belum terdaftar")

        if not verify_password(form_data.password, db_user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password salah")

        access_token = create_access_token(subject=str(db_user.id), expires_delta=timedelta(minutes=15))
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Login failed: {str(e)}") from e
