from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DELTA
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: timedelta = ACCESS_TOKEN_EXPIRE_DELTA) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode({"sub": subject, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_user(user: models.User | None = Depends(get_current_user)) -> models.User:
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user

def require_admin(user: models.User = Depends(require_user)) -> models.User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
