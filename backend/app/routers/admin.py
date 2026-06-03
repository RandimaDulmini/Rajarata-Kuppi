from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/students", response_model=list[schemas.UserOut])
def list_students(db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    return db.query(models.User).filter(models.User.role == 'student').all()

@router.patch("/users/{user_id}/promote")
def promote_user(user_id: int, db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    u = db.get(models.User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.role = 'admin'
    db.add(u); db.commit(); db.refresh(u)
    return {"ok": True}
