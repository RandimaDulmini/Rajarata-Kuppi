from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import create_access_token, hash_password, verify_password, require_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = models.User(**payload.model_dump(exclude={"password"}), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(require_user)):
    return user
