from fastapi import FastAPI
from src.routes.graphql import graphql_app

app = FastAPI(title="Auth Service")
app.include_router(graphql_app, prefix="/graphql")