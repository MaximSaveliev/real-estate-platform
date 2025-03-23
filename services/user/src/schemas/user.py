import strawberry
from typing import Optional, List
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from config.db import database
from config.settings import get_settings
import uuid
from src.middleware.auth import graphql_requires_roles

settings = get_settings()
NAMESPACE_DNS = uuid.UUID(str(settings.NAMESPACE_DNS))

# Add this helper function
async def get_role_name(role_id: int) -> str:
    """Get role name from role ID"""
    # Simple mapping for common roles
    roles = {
        1: "admin",
        2: "agency_admin",
        3: "agent",
        4: "user"
    }
    
    return roles.get(role_id, "unknown")

@strawberry.type
class User:
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    is_active: bool
    role_id: int

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from User Service!"
    
    @strawberry.field
    @graphql_requires_roles(["admin", "agency_admin"])  # Protected query - only admin and agency_admin can access
    async def get_all_users(self, info) -> List[User]:
        current_user = info.context.get("user")
        
        # Get all users from database
        users_data = await run_in_threadpool(database.get_all_users)
        
        # Convert to User type
        return [
            User(
                id=user["id"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                phone=user.get("phone"),
                profile_image_url=user.get("profile_image_url"),
                bio=user.get("bio"),
                is_verified=user["is_verified"],
                is_active=user["is_active"],
                role_id=user["role_id"]
            )
            for user in users_data
        ]
    
    @strawberry.field
    async def get_user(self, id: str) -> Optional[User]:
        result = await run_in_threadpool(database.get_user_by_id, id)
        if not result:
            return None
        
        return User(
            id=result["id"],
            email=result["email"],
            first_name=result["first_name"],
            last_name=result["last_name"],
            phone=result.get("phone"),
            profile_image_url=result.get("profile_image_url"),
            bio=result.get("bio"),
            is_verified=result["is_verified"],
            is_active=result["is_active"],
            role_id=result["role_id"]
        )
    
    @strawberry.field
    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await run_in_threadpool(database.get_user_by_email, email)
        if not result:
            return None
        
        return User(
            id=result["id"],
            email=result["email"],
            first_name=result["first_name"],
            last_name=result["last_name"],
            phone=result.get("phone"),
            profile_image_url=result.get("profile_image_url"),
            bio=result.get("bio"),
            is_verified=result["is_verified"],
            is_active=result["is_active"],
            role_id=result["role_id"]
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        bio: Optional[str] = None
    ) -> User:
        try:
            # Generate UUIDv5 using DNS namespace and email for consistent ID generation
            user_id = str(uuid.uuid5(NAMESPACE_DNS, email))
            
            # Get the default role_id for regular users
            role_id = await run_in_threadpool(database.ensure_default_role)
            
            # Create the user
            result = await run_in_threadpool(
                database.create_user,
                user_id,
                email,
                password_hash,
                first_name,
                last_name,
                role_id,
                phone,
                profile_image_url,
                bio
            )
            
            if not result:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            return User(
                id=result["id"],
                email=result["email"],
                first_name=result["first_name"],
                last_name=result["last_name"],
                phone=result.get("phone"),
                profile_image_url=result.get("profile_image_url"),
                bio=result.get("bio"),
                is_verified=False,
                is_active=True,
                role_id=role_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
            
    @strawberry.mutation
    @graphql_requires_roles(["admin", "user"])  # Protected mutation - only admin or the user themselves can update
    async def update_user_profile(
        self,
        info,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        profile_image_url: Optional[str] = None,
        bio: Optional[str] = None
    ) -> User:
        try:
            # Get current user from context
            current_user = info.context.get("user")
            if not current_user:
                # Try getting via the function
                current_user = await info.context["get_current_user"]()
                
            # Check if user is updating their own profile or is an admin
            role = current_user.get("role", "user")
            if role != "admin" and str(current_user.get("id")) != user_id:
                raise HTTPException(status_code=403, detail="You can only update your own profile")
            
            # Update user in database
            result = await run_in_threadpool(
                database.update_user,
                user_id,
                first_name,
                last_name,
                phone,
                profile_image_url,
                bio
            )
            
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            return User(
                id=result["id"],
                email=result["email"],
                first_name=result["first_name"],
                last_name=result["last_name"],
                phone=result.get("phone"),
                profile_image_url=result.get("profile_image_url"),
                bio=result.get("bio"),
                is_verified=result["is_verified"],
                is_active=result["is_active"],
                role_id=result["role_id"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
