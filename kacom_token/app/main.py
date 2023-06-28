import os

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from starlette.config import Config

from .database import get_db
from .router import router

if os.path.exists(".env.local"):
    env_file = ".env.local"
    config = Config(env_file)
    ENVIRONMENT = config("ENVIRONMENT")
else:
    ENVIRONMENT = os.environ.get("ENVIRONMENT")

SHOW_DOCS_ENVIRONMENT = ("local", "staging")
app_configs = {"title": "Kacom API v1.0"}
if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI()

app.include_router(router, prefix="/api/v1/token", tags=["login"])


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    dependencies = {}
    try:
        if db.is_active:
            dependencies["mysql"] = {"status": "ok", "details": "Connected to MySQL"}
        else:
            dependencies["mysql"] = {"status": "error", "details": "Failed to Connect"}
    except Exception as e:
        dependencies["mysql"] = {"status": "error", "details": str(e)}

    status = (
        "ok" if all(dep["status"] == "ok" for dep in dependencies.values()) else "error"
    )
    return {"status": status, "dependencies": dependencies}
