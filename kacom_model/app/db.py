from functools import lru_cache

import motor.motor_asyncio
from bson import ObjectId
from pydantic import BaseModel, Field

from .config import Settings

settings = Settings()
mongodb_url = settings.mongodb_url

client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
db = client.kacom
