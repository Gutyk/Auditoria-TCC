# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import User
from ..schemas import TokenRequest, TokenResponse
from ..utils.security import create_access_token, hash_password, verify_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_user():
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email="admin@local").first():
            u = User(email="admin@local", password_hash=hash_password("admin"))
            db.add(u)
            db.commit()
    finally:
        db.close()

@router.post("/token", response_model=TokenResponse)
def login(data: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=user.email)
    return TokenResponse(access_token=token)
