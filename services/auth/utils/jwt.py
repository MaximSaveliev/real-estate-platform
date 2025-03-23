import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from config.settings import settings

def create_jwt_token(data: dict) -> str:
    payload = data | {"exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=settings.ALGORITHM)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")