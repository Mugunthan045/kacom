from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .config import Settings
from .exceptions import INVALID_TOKEN_EXCEPTION

settings = Settings()

jwtpublickey = settings.public_key
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, jwtpublickey, algorithms=["RS256"])
        return payload
    except JWTError:
        raise INVALID_TOKEN_EXCEPTION
