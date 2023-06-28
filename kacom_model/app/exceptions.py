from fastapi import HTTPException, status
from starlette.requests import Request
from starlette.responses import JSONResponse

UNSUPPORTED_MEDIA_EXCEPTION = JSONResponse(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    content={"message": "unsupported media type"},
)
CONTENT_NOTFOUND_EXCEPTION = JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND, content={"message": "not found"}
)
VERSION_CONFLICT_EXCEPTION = JSONResponse(
    status_code=status.HTTP_409_CONFLICT, content={"message": "version conflict"}
)

INVALID_TOKEN_EXCEPTION = JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "invalid token"}
)
