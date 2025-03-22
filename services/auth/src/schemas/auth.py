import strawberry
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from config.settings import get_settings
from config.redis import RedisService
from config.rabbitmq import RabbitMQService
from src.utils.jwt import create_jwt_token, create_refresh_token, create_session_token
from src.utils.password import hash_password
import httpx
import json
from datetime import datetime, timedelta

settings = get_settings()

@strawberry.type
class TokenResponse:
    access_token: str
    refresh_token: str
    session_token: str
    token_type: str

@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from Auth Service!"

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def signup(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        info: strawberry.Info
    ) -> TokenResponse:
        # Get services from context
        redis = info.context["redis"]
        rabbitmq = info.context["rabbitmq"]
        
        # Call User Service to create user (via GraphQL)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/graphql",
                json={
                    "query": """
                        mutation CreateUser($email: String!, $password: String!, $firstName: String!, $lastName: String!, $role: String!, $permissions: [String!]!) {
                            createUser(email: $email, password: $password, firstName: $firstName, lastName: $lastName, role: $role, permissions: $permissions) {
                                id
                            }
                        }
                    """,
                    "variables": {
                        "email": email,
                        "password": hash_password(password),
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": "user",
                        "permissions": ["read:own", "write:own"]
                    }
                }
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to create user")

            data = response.json()
            if "errors" in data:
                raise HTTPException(status_code=400, detail=data["errors"])
            user_id = data["data"]["createUser"]["id"]

        # Generate tokens
        access_token = create_jwt_token(
            user_id, email, "user", ["read:own", "write:own"],
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token()
        session_token = create_session_token()

        # Store tokens in Redis
        await redis.set(f"refresh:{refresh_token}", user_id, ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        await redis.set(f"session:{session_token}", user_id, ex=settings.SESSION_TOKEN_EXPIRE_DAYS * 86400)
        await redis.set(f"session:{session_token}:last_login", datetime.utcnow().isoformat(), ex=settings.SESSION_TOKEN_EXPIRE_DAYS * 86400)

        # Send verification email via RabbitMQ
        email_message = json.dumps({
            "email": email,
            "user_id": user_id,
            "verify_url": f"http://your-app/verify-email?token={user_id}"
        })
        await rabbitmq.publish("email-verification", email_message)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            session_token=session_token,
            token_type="bearer"
        )