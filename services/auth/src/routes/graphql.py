import strawberry
from fastapi import Depends, APIRouter
from strawberry.fastapi import GraphQLRouter
from functools import lru_cache
from typing import AsyncGenerator, Dict, Any

from src.schemas.auth import Query, Mutation
from config.redis import RedisService
from config.rabbitmq import RabbitMQService

async def get_redis() -> AsyncGenerator[RedisService, None]:
    redis_service = RedisService()
    try:
        yield redis_service
    finally:
        await redis_service.close()

async def get_rabbitmq() -> AsyncGenerator[RabbitMQService, None]:
    rabbitmq_service = RabbitMQService()
    await rabbitmq_service.connect()
    try:
        yield rabbitmq_service
    finally:
        await rabbitmq_service.close()

async def get_context(
    redis: RedisService = Depends(get_redis), 
    rabbitmq: RabbitMQService = Depends(get_rabbitmq)) -> Dict[str, Any]:
    return {"redis": redis, "rabbitmq": rabbitmq}

# Create schema once during module initialization
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# Create a FastAPI router and include the GraphQL app
router = APIRouter()
router.include_router(graphql_app, prefix="/graphql")