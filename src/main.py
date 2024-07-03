from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.topic_router import topic_router_v1
from src.routers.user_router import user_router_v1


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


