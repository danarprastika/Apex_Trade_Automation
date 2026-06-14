from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.rate_limit import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.database.base import get_db
from app.database.models.identity import UserRole
from app.database.repositories.user_repository import create_user, get_user_by_email, get_user_by_username

router = APIRouter()


@router.post("/register")
def register(email: str, username: str, password: str, db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if get_user_by_username(db, username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    password_hash = hash_password(password)
    user = create_user(db, email=email, username=username, password_hash=password_hash, role=UserRole.TRADER)
    return {"success": True, "message": "User registered", "data": {"user_id": str(user.id)}}


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=15))
    return {"success": True, "message": "Login successful", "data": {"access_token": access_token}}
