from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, require_user

router = APIRouter(prefix="/forum", tags=["Forum"])

@router.get("/posts", response_model=list[schemas.ForumPostOut])
def list_posts(db: Session = Depends(get_db), user: models.User | None = Depends(get_current_user)):
    q = db.query(models.ForumPost).order_by(models.ForumPost.created_at.desc())
    # admins can see everything
    if user and user.role == 'admin':
        return q.all()
    # if not logged in, return empty list
    if not user:
        return []
    # students: return posts where module_code matches modules they are enrolled in
    enrolled = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id).all()
    mod_ids = [e.module_id for e in enrolled]
    if not mod_ids:
        return []
    mods = db.query(models.Module).filter(models.Module.id.in_(mod_ids)).all()
    mod_codes = [m.code for m in mods]
    return q.filter(models.ForumPost.module_code.in_(mod_codes)).all()

@router.post("/posts", response_model=schemas.ForumPostOut, status_code=201)
def create_post(payload: schemas.ForumPostCreate, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    # require module_code and ensure student is enrolled in that module
    if not payload.module_code:
        raise HTTPException(status_code=400, detail="module_code is required for forum posts")
    mod = db.query(models.Module).filter(models.Module.code == payload.module_code).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
    if user.role != 'admin':
        enrolled = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == mod.id).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Only enrolled students can post questions for this module")
    post = models.ForumPost(**payload.model_dump(), author_id=user.id)
    db.add(post); db.commit(); db.refresh(post)
    return post

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.ForumPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    replies = db.query(models.ForumReply).filter(models.ForumReply.post_id == post_id).order_by(models.ForumReply.created_at).all()
    return {"post": post, "replies": replies}

@router.post("/posts/{post_id}/replies", response_model=schemas.ReplyOut, status_code=201)
def create_reply(post_id: int, payload: schemas.ReplyCreate, db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    if not db.get(models.ForumPost, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    post = db.get(models.ForumPost, post_id)
    # if student, ensure they are enrolled in the post's module
    if user.role != 'admin' and post.module_code:
        mod = db.query(models.Module).filter(models.Module.code == post.module_code).first()
        if not mod:
            raise HTTPException(status_code=404, detail="Module not found")
        enrolled = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.module_id == mod.id).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Only enrolled students can reply to this post")
    reply = models.ForumReply(post_id=post_id, body=payload.body, author_id=user.id)
    db.add(reply); db.commit(); db.refresh(reply)
    return reply
