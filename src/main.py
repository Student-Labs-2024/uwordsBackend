from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users import FastAPIUsers

from src.database.db_config import User
from src.routers.topic_router import topic_router_v1
from src.routers.user_router import user_router_v1
from src.schemes.schemas import UserCreate, UserRead, UserUpdate
from src.utils.user import get_user_manager, auth_backend


tags_metadata = [
    {
        "name": "User Words",
        "description": "Operations with user's words",
    }
]

app = FastAPI(
    title="UWords FastAPI",
    description="API of UWords - application for learning English",
    openapi_tags=tags_metadata
)

origins = [
    "http://localhost:5173",
    "https://localhost:5173",
    "http://localhost",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router_v1)
app.include_router(topic_router_v1)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1/users/auth",
    tags=["User Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/users/auth",
    tags=["User Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["User Router"],
)

