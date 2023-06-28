from datetime import datetime, timedelta
from typing import Union

from jose import JWTError, jwt

from .config import Settings

settings = Settings()

jwtprivatekey = settings.private_key
jwtpublickey = settings.public_key
jwtexpiry = settings.expiry_time
jwtrefreshexpiry = settings.refresh_expiry_time
jwtalgorithm = settings.algorithm


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, jwtprivatekey, algorithm=jwtalgorithm)
    return encoded_jwt


def create_refresh_token(username):
    expire = timedelta(minutes=jwtrefreshexpiry)
    return create_access_token(data={"sub": username}, expires_delta=expire)


def decode_token(token):
    return jwt.decode(token, jwtpublickey, algorithms=jwtalgorithm)
