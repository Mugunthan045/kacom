from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .exceptions import CREDENTIAL_EXCEPTION
from .models import TokenData
from .schemas import User
from .services import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise CREDENTIAL_EXCEPTION
        token_data = TokenData(username=username)
    except JWTError:
        pass
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise CREDENTIAL_EXCEPTION
    return user
