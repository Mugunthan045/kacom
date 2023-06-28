from .config import Settings
from redis import Redis

settings = Settings()

redis_client = Redis(host=settings.redis_host, port=6379)
