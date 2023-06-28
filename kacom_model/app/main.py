import os
from functools import lru_cache

from fastapi import Depends, FastAPI
from starlette.config import Config

from .config import Settings, get_settings
from .db import client
from .routers import pickle
from .redis_client import redis_client

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

app = FastAPI(**app_configs)

app.include_router(pickle.router, prefix="/api/v1/pickle", tags=["pickle"])


@app.get("/health")
async def health():
    dependencies = {}
    try:
        await client.server_info()
        dependencies["mongodb"] = {"status": "ok", "details": "Connected to MongoDB"}
    except Exception as e:
        dependencies["mongodb"] = {"status": "error", "details": str(e)}
    try:
        redis_client.ping()
        dependencies["redis"] = {"status": "ok", "details": "Connected to Redis"}
    except Exception as e:
        dependencies["redis"] = {"status": "error", "details": str(e)}

    status = (
        "ok" if all(dep["status"] == "ok" for dep in dependencies.values()) else "error"
    )
    return {"status": status, "dependencies": dependencies}
