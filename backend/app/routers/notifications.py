from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=list[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    return db.query(models.Notification).order_by(models.Notification.created_at.desc()).all()

@router.post("", response_model=schemas.NotificationOut, status_code=201)
def create_notification(payload: schemas.NotificationCreate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    item = models.Notification(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.patch("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Notification, notification_id)
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")
    item.is_read = True
    db.commit(); db.refresh(item)
    return item

@router.patch("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(models.Notification).update({models.Notification.is_read: True})
    db.commit()
    return {"message": "All notifications marked as read"}
