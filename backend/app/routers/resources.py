from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from .. import models, schemas
from ..config import UPLOAD_DIR
from ..database import get_db
from ..security import require_admin, require_user

router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get("", response_model=list[schemas.ResourceOut])
def list_resources(
    resource_type: str | None = Query(None),
    department: str | None = Query(None),
    module_code: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(models.Resource)
    if resource_type:
        q = q.filter(models.Resource.resource_type == resource_type)
    if department:
        q = q.filter(models.Resource.department_code == department.upper())
    if module_code:
        q = q.filter(models.Resource.module_code == module_code)
    if search:
        like = f"%{search}%"
        q = q.filter(models.Resource.title.ilike(like) | models.Resource.description.ilike(like))
    return q.order_by(models.Resource.created_at.desc()).limit(limit).all()

@router.post("", response_model=schemas.ResourceOut, status_code=201)
def create_resource(payload: schemas.ResourceCreate, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    # Admins can create freely; students must specify a module_code and be enrolled in it.
    if user.role != 'admin':
        if not payload.module_code:
            raise HTTPException(status_code=400, detail="Students must specify module_code when creating resources")
        mod = db.query(models.Module).filter(models.Module.code == payload.module_code).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Module not found")
        enrolled = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == mod.id).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="You must be enrolled in the module to add resources")
    item = models.Resource(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.post("/upload", response_model=schemas.ResourceOut, status_code=201)
async def upload_resource(
    title: str,
    department_code: str,
    resource_type: str,
    module_code: str | None = None,
    description: str | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_user),
):
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.bin").suffix
    safe_name = f"{uuid4().hex}{suffix}"
    path = Path(UPLOAD_DIR) / safe_name
    content = await file.read()
    path.write_bytes(content)
    # if uploader is student, require enrollment in module_code
    if user.role != 'admin':
        if not module_code:
            raise HTTPException(status_code=400, detail="Students must specify module_code when uploading resources")
        mod = db.query(models.Module).filter(models.Module.code == module_code).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Module not found")
        enrolled = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == mod.id).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="You must be enrolled in the module to upload resources")

    item = models.Resource(
        title=title,
        department_code=department_code.upper(),
        module_code=module_code,
        resource_type=resource_type,
        file_type=suffix.replace('.', '').upper() or "FILE",
        description=description,
        file_url=f"/uploads/{safe_name}",
        is_new=True,
    )
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.post("/{resource_id}/download", response_model=schemas.ResourceOut)
def count_download(resource_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Resource, resource_id)
    if not item:
        raise HTTPException(status_code=404, detail="Resource not found")
    item.downloads += 1
    db.commit(); db.refresh(item)
    return item
