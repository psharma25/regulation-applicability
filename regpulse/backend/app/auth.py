"""Authentication: bcrypt password hashing + JWT bearer tokens (open source)."""
import datetime as dt
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from . import models

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(p.encode("utf-8")[:72], h.encode("utf-8"))
    except Exception:
        return False


def create_token(sub: str) -> str:
    exp = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": sub, "exp": exp}, settings.SECRET_KEY, algorithm="HS256")


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> models.User:
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Not authenticated",
                             headers={"WWW-Authenticate": "Bearer"})
    if not token:
        raise cred_exc
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
    except JWTError:
        raise cred_exc
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise cred_exc
    return user
