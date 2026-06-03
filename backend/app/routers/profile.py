from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=schemas.UserOut)
def get_profile(user: models.User = Depends(require_user)):
    return user

@router.put("", response_model=schemas.UserOut)
def update_profile(payload: schemas.UserUpdate, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit(); db.refresh(user)
    return user
