import redis
from config.settings import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_INDEX,
    password=settings.REDIS_PASS  # Match Docker Compose password
)