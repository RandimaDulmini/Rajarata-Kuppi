from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/home")
def home_stats(db: Session = Depends(get_db)):
    return {
        "students": db.query(models.User).count(),
        "departments": db.query(models.Department).count(),
        "modules": db.query(models.Module).count(),
        "resources": db.query(models.Resource).count(),
        "unread_notifications": db.query(models.Notification).filter(models.Notification.is_read == False).count(),
    }
