import traceback
from datetime import datetime, timedelta
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import EmailStr
from sqlalchemy.orm import Session

from .config import Settings
from .database import get_db
from .dependencies import get_current_active_user
from .exceptions import *
from .models import Token, TokenData
from .models import User as UserSchema
from .models import UserInDB
from .schemas import User
from .services import create_access_token, create_refresh_token, decode_token
from .utils import hash_password, verify_password

settings = Settings()

jwtexpiry = settings.expiry_time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


def create_token(username):
    access_token_expiry = timedelta(minutes=jwtexpiry)
    return create_access_token(
        data={"sub": username}, expires_delta=access_token_expiry
    )


def authenticate(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/register")
async def create_user(user: UserInDB, db: Session = Depends(get_db)):
    try:
        user_indb = (
            db.query(User).filter(User.email == EmailStr(user.email.lower())).first()
        )
        if user_indb:
            raise EMAIL_CONFLICT_EXCEPTION
        username_check = db.query(User).filter(User.username == user.username).first()
        if username_check:
            raise USERNAME_CONFLICT_EXCEPTION
        user.password = hash_password(user.password)
        user.email = EmailStr(user.email.lower())
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Account created"}
    except Exception():
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "error creating user"})


@router.get("/validate", response_model=UserSchema)
async def read_user(current_user: User = Depends(get_current_active_user)):
    return {"username": current_user.username, "email": current_user.email}


@router.post("/token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        username = form_data.username
        password = form_data.password
        user = authenticate(username, password, db)
        if not user:
            raise CREDENTIAL_EXCEPTION
        access_token = create_token(username)
        refresh_token = create_refresh_token(username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception():
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "error generating token"}
        )


@router.post("/refresh")
async def refresh(grant_type: str = Form(...), refresh_token: str = Form(...)):
    try:
        if grant_type == "refresh_token":
            token = refresh_token
            payload = decode_token(token)
            if datetime.utcfromtimestamp(payload.get("exp")) > datetime.utcnow():
                username = payload.get("sub")
                print(payload.get("exp"))
                access_token = create_token(username)
                return {"access_token": access_token}
    except Exception:
        traceback.print_exc()
        return {"message": "false"}
