import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from src.schemas.user import Query, Mutation
from src.middleware.auth import get_user_from_context

async def get_context(request: Request):
    # Simplified context creator that can be awaited
    return {
        "request": request,
        "get_current_user": lambda: get_user_from_context({"context": {"request": request}}),
    }

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)