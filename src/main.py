import sentry_sdk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.mail_router import mail_router_v1
from src.routers.payment_router import payment_router_v1
from src.routers.subscription_routers import subscription_router_v1
from src.routers.user_router import user_router_v1
from src.routers.topic_router import topic_router_v1
from src.routers.auth_router import auth_router_v1
from src.routers.admin_router import admin_router_v1
from src.routers.websocket_router import websocket_router_v1, add_error_router
from src.routers.achievement_router import achievement_router_v1

from src.config.instance import ALLOWED_ORIGINS_LIST, SENTRY_URL
from src.config.fastapi_docs_config import TAGS_METADATA

sentry_sdk.init(
    dsn=SENTRY_URL,
    traces_sample_rate=1.0,
)

app = FastAPI(
    title="UWords FastAPI",
    description="API of UWords - application for learning English",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router_v1)
app.include_router(topic_router_v1)
app.include_router(websocket_router_v1)
app.include_router(add_error_router)
app.include_router(auth_router_v1)
app.include_router(admin_router_v1)
app.include_router(mail_router_v1)
app.include_router(payment_router_v1)
app.include_router(subscription_router_v1)
app.include_router(achievement_router_v1)
