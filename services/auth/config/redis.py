import redis.asyncio as redis
from config.settings import get_settings
from typing import Optional

settings = get_settings()

class RedisService:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        await self.client.set(key, value, ex=ex)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def close(self):
        await self.client.close()