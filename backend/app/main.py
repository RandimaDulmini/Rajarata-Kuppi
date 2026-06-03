from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import APP_NAME, FRONTEND_ORIGIN, UPLOAD_DIR
from .database import Base, engine, SessionLocal
from .seed import seed
from .routers import auth, forum, gpa, modules, notifications, profile, resources, stats, support, enrollments
from .routers import admin

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed(db)

app = FastAPI(title=APP_NAME, version="1.0.0")

origins = ["*"] if FRONTEND_ORIGIN == "*" else [FRONTEND_ORIGIN, "http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def root():
    return {"message": "Rajarata Kuppi FastAPI backend is running", "docs": "/docs"}

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(modules.router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(gpa.router, prefix="/api")
app.include_router(forum.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(support.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(enrollments.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
