import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Kacom API"
    mongodb_url: str
    public_key: str
    redis_host: str

    class Config:
        if os.path.exists(".env.local"):
            env_file = ".env.local"
        else:
            mongodb_url = os.environ.get("MONGODB_URL")
            public_key = os.environ.get("PUBLIC_KEY")
            redis_host = os.environ.get("REDIS_HOST")
        

@lru_cache()
def get_settings():
    return Settings()
