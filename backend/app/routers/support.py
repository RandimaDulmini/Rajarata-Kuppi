from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/support", tags=["Support"])

@router.post("/messages", response_model=schemas.SupportMessageOut, status_code=201)
def create_support_message(payload: schemas.SupportMessageCreate, db: Session = Depends(get_db)):
    item = models.SupportMessage(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/messages", response_model=list[schemas.SupportMessageOut])
def list_support_messages(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(models.SupportMessage).order_by(models.SupportMessage.created_at.desc()).all()
