import os
from datetime import timedelta

APP_NAME = os.getenv("APP_NAME", "Rajarata Kuppi API")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rajarata_kuppi.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
