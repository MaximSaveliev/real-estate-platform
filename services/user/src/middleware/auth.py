from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List, Callable
import httpx
from functools import wraps
from config.settings import get_settings

settings = get_settings()
security = HTTPBearer()

class AuthServiceClient:
    """Client for communicating with the Auth Service"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or settings.AUTH_SERVICE_URL
        
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token with the auth service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/verify-token",
                    json={"token": token}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication token",
                    )
                    
                return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service unavailable: {str(e)}",
            )
    
    async def check_permission(self, token: str, resource: str, action: str) -> bool:
        """Check if a user has permission to perform an action on a resource"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/check-permission",
                    json={"token": token, "resource": resource, "action": action}
                )
                
                if response.status_code != 200:
                    return False
                    
                data = response.json()
                return data.get("has_permission", False)
        except httpx.HTTPError:
            return False

# Create a global client instance
auth_client = AuthServiceClient()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token with auth service and return the user data
    This is used as a FastAPI dependency
    """
    token = credentials.credentials
    
    # Verify token with auth service
    user_data = await auth_client.verify_token(token)
    return user_data

def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Create a dependency that requires specific roles
    Example: @app.get("/admin", dependencies=[Depends(require_roles(["admin"]))])
    """
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        
        # Verify token with auth service
        user_data = await auth_client.verify_token(token)
        
        # Check if user has required role
        role = user_data.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires one of these roles: {', '.join(allowed_roles)}",
            )
        return user_data
    
    return role_checker

# GraphQL-specific auth helpers
async def get_user_from_context(info):
    """Extract user from GraphQL context"""
    request = info.context.get("request")
    if not request:
        return None
        
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
        
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Verify token with auth service
        user_data = await auth_client.verify_token(token)
        return user_data
    except Exception:
        return None

def graphql_requires_roles(allowed_roles: List[str]):
    """
    Decorator for GraphQL resolver functions that require specific roles
    """
    def decorator(resolver):
        @wraps(resolver)
        async def wrapper(root, info, **kwargs):
            # Get authorization header
            request = info.context.get("request")
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
                
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
                
            token = auth_header.replace("Bearer ", "")
            
            # Verify token with auth service
            user_data = await auth_client.verify_token(token)
            
            # Check if user has required role
            role = user_data.get("role")
            if role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This operation requires one of these roles: {', '.join(allowed_roles)}",
                )
                
            # Add user to context
            info.context["user"] = user_data
                
            return await resolver(root, info, **kwargs)
        return wrapper
    return decorator