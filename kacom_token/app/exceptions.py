from fastapi import HTTPException, status

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

EMAIL_CONFLICT_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Accout already exist"
)

USERNAME_CONFLICT_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Username already taken, try another"
)
