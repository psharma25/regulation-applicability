"""Auth routes: register, login (OAuth2 password flow), current user."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = models.User(email=body.email, password_hash=auth.hash_password(body.password))
    db.add(user)
    db.commit()
    return schemas.Token(access_token=auth.create_token(user.email))


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return schemas.Token(access_token=auth.create_token(user.email))


@router.get("/me")
def me(user: models.User = Depends(auth.current_user)):
    return {"id": user.id, "email": user.email}
