from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_user, require_admin

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post("", response_model=schemas.EnrollmentOut, status_code=201)
def enroll(payload: dict, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    # payload should contain module_id or module_code
    module = None
    if 'module_id' in payload:
        module = db.get(models.Module, int(payload['module_id']))
    elif 'module_code' in payload:
        module = db.query(models.Module).filter(models.Module.code == payload['module_code']).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    # prevent duplicate
    existing = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == module.id).first()
    if existing:
        return existing
    enr = models.Enrollment(user_id=user.id, module_id=module.id)
    db.add(enr); db.commit(); db.refresh(enr)
    return enr

@router.delete("/{module_id}")
def unenroll(module_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    enr = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == module_id).first()
    if not enr:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enr); db.commit()
    return {"ok": True}

@router.get("", response_model=list[schemas.EnrollmentOut])
def my_enrollments(db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    return db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id).all()

@router.get("/all", response_model=list[schemas.EnrollmentOut])
def all_enrollments(db: Session = Depends(get_db), _admin: models.User = Depends(require_admin)):
    return db.query(models.Enrollment).order_by(models.Enrollment.created_at.desc()).all()
