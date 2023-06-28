import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Kacom API"
    sqlalchemy_database_uri: str
    algorithm: str
    expiry_time: int
    refresh_expiry_time: int
    private_key: str
    public_key: str

    class Config:
        if os.path.exists(".env.local"):
            env_file = ".env.local"
        else:
            sqlalchemy_database_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")
            algorithm = os.environ.get("ALGORITHM")
            expirty_time = os.environ.get("EXPIRY_TIME")
            refresh_expiry_time = os.environ.get("REFRESH_EXPIRTY_TIME")
            private_key = os.environ.get("PRIVATE_KEY")


@lru_cache()
def get_settings():
    return Settings()
