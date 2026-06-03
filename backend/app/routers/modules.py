from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import require_admin, get_current_user

router = APIRouter(tags=["Departments & Modules"])

@router.get("/departments", response_model=list[schemas.DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).order_by(models.Department.code).all()

@router.get("/modules", response_model=list[schemas.ModuleOut])
def list_modules(department: str | None = Query(None), year: str | None = Query(None), db: Session = Depends(get_db), user: models.User | None = Depends(get_current_user)):
    q = db.query(models.Module)
    if department:
        code = department.upper()
        q = q.outerjoin(models.Module.departments).filter((models.Module.department_code == code) | (models.Department.code == code)).distinct()
    else:
        # students (non-admin) see modules for their department by default
        if user and user.role != 'admin' and user.department_code:
            code = user.department_code.upper()
            # include modules where module.department_code == code OR modules linked via module_departments association
            q = q.outerjoin(models.Module.departments).filter((models.Module.department_code == code) | (models.Department.code == code)).distinct()
    if year:
        q = q.filter(models.Module.year == year)
    return q.order_by(models.Module.department_code, models.Module.code).all()


@router.get("/modules/{module_id}", response_model=schemas.ModuleOut)
def get_module(module_id: int, db: Session = Depends(get_db)):
    m = db.get(models.Module, module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")
    return m

@router.post("/modules", response_model=schemas.ModuleOut, status_code=201)
def create_module(payload: schemas.ModuleCreate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    if db.query(models.Module).filter(models.Module.code == payload.code).first():
        raise HTTPException(status_code=409, detail="Module code already exists")
    # create module and associate it with the departments that are allowed to enroll
    data = payload.model_dump(exclude={"departments"})
    item = models.Module(**data)
    allowed_codes = [payload.department_code, *(payload.departments or [])]
    deps = []
    seen = set()
    for code in allowed_codes:
        normalized = code.upper()
        if normalized in seen:
            continue
        department = db.query(models.Department).filter(models.Department.code == normalized).first()
        if not department:
            raise HTTPException(status_code=400, detail=f"Department not found: {normalized}")
        deps.append(department)
        seen.add(normalized)
    if not deps:
        raise HTTPException(status_code=400, detail="At least one department must be selected for the module")
    item.departments = deps
    db.add(item); db.commit(); db.refresh(item)
    return item
