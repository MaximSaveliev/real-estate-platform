from fastapi import FastAPI, Depends
from src.routes.graphql import graphql_app
from config.db import database
from contextlib import asynccontextmanager
import logging
from src.middleware.auth import require_roles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("user-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to database on startup
    logger.info("Starting User Service...")
    database.connect()
    database.create_tables()
    database.ensure_default_role()
    logger.info("User Service started and connected to PostgreSQL")
    yield
    # Disconnect on shutdown
    database.disconnect()
    logger.info("User Service stopped and disconnected from PostgreSQL")

app = FastAPI(
    title="User Service",
    description="User management service for Real Estate Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add GraphQL route
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

# Protected endpoint example
# @app.get("/admin/users", dependencies=[Depends(require_roles(["admin"]))])
# async def admin_get_users():
#     """Admin-only endpoint to get all users"""
#     return {"message": "This endpoint is admin-only"}