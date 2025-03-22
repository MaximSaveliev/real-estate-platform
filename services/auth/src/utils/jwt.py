import jwt
from datetime import datetime, timedelta
import secrets
from config.settings import get_settings
from typing import Dict, List, Optional

settings = get_settings()

def create_jwt_token(user_id: str, email: str, role: str, permissions: List[str], expires_delta: timedelta) -> str:
    to_encode = {
        "sub": user_id,
        "email": email,
        "role": role,
        "permissions": permissions,
        "iss": settings.ISSUER,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + expires_delta).timestamp())
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def decode_jwt_token(token: str) -> Dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        raise ValueError("Invalid token")

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def create_session_token() -> str:
    return secrets.token_urlsafe(32)