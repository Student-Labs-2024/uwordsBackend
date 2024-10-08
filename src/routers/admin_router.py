from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta

from fastapi.security import HTTPBearer
from fastapi import APIRouter, Depends

from src.database.models import User
from src.schemes.admin_schemas import AdminCreate, AdminEmailLogin

from src.schemes.enums.enums import Providers
from src.schemes.user_schemas import UserData, UserDump
from src.schemes.util_schemas import TokenInfo, CustomResponse

from src.services.subscription_service import SubscriptionService
from src.services.user_service import UserService

from src.utils import auth as auth_utils
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric

from src.config.instance import (
    ADMIN_SECRET,
    ALLOWED_AUDIO_SECONDS,
    ALLOWED_VIDEO_SECONDS,
    DEFAULT_ENERGY,
    METRIC_URL,
)
from src.config import fastapi_docs_config as doc_data
from src.utils.exceptions import (
    AdminAlreadyExistsException,
    IncorrectAdminKeyException,
    SubscriptionNotFoundException,
    UserNotFoundException,
)
from src.utils.metric import get_user_metric
from src.utils.logger import admin_router_logger


http_bearer = HTTPBearer()
admin_router_v1 = APIRouter(prefix="/api/users", tags=["Admins"])


@admin_router_v1.post(
    "/admin/register",
    response_model=UserDump,
    name=doc_data.ADMIN_REGISTER_TITLE,
    description=doc_data.ADMIN_REGISTER_DESCRIPTION,
)
async def create_admin(
    admin_data: AdminCreate,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    if await user_service.get_user_by_provider(
        unique=admin_data.email, provider=Providers.admin.value, user_field=User.email
    ):
        raise AdminAlreadyExistsException(email=admin_data.email)

    if not admin_data.admin_secret == ADMIN_SECRET:
        raise IncorrectAdminKeyException()

    user = await user_service.create_user(
        data=admin_data, provider=Providers.admin.value
    )

    user.metrics = await get_user_metric(
        user_id=user.id,
        user_days=user.days,
        uwords_uid=user.uwords_uid,
        server_url=METRIC_URL,
    )

    return user


@admin_router_v1.post(
    "/admin/login",
    response_model=TokenInfo,
    name=doc_data.ADMIN_LOGIN_TITLE,
    description=doc_data.ADMIN_LOGIN_DESCRIPTION,
)
async def user_login(
    login_data: AdminEmailLogin,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    return await user_service.auth_user(
        provider=Providers.admin.value, login_data=login_data
    )


@admin_router_v1.delete(
    "/{user_id}/ban",
    response_model=CustomResponse,
    name=doc_data.USER_BAN_TITLE,
    description=doc_data.USER_BAN_DESCRIPTION,
)
async def ban_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    await user_service.ban_user(user_id=user_id)

    return CustomResponse(status_code=200, message=f"User {user_id} banned succesfully")


@admin_router_v1.delete(
    "/{user_id}/delete",
    response_model=CustomResponse,
    name=doc_data.USER_DELETE_TITLE,
    description=doc_data.USER_DELETE_DESCRIPTION,
)
async def ban_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    await user_service.delete_user(user_id=user_id)

    return CustomResponse(
        status_code=200, message=f"User {user_id} deleted succesfully"
    )


@admin_router_v1.get(
    "/{user_id}/reset-limits",
    response_model=CustomResponse,
    name=doc_data.USER_RESET_TITLE,
    description=doc_data.USER_RESET_DESCRIPTION,
)
async def reset_user_limits(
    user_id: int,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    await user_service.update_user(
        user_id=user_id,
        user_data={
            "allowed_audio_seconds": ALLOWED_AUDIO_SECONDS,
            "allowed_video_seconds": ALLOWED_VIDEO_SECONDS,
            "energy": DEFAULT_ENERGY,
        },
    )

    return CustomResponse(
        status_code=200, message=f"Limits for user {user_id} reseted succesfully"
    )


@admin_router_v1.get(
    "/{user_id}/sub",
    response_model=UserData,
    name=doc_data.USER_SUB_TITLE,
    description=doc_data.USER_SUB_DESCRIPTION,
)
async def give_user_sub(
    user_id: int,
    sub_id: int,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    user = await user_service.get_user_by_id(user_id=user_id)
    if not user:
        raise UserNotFoundException()

    subscription = await sub_service.get_sub_by_id(id=sub_id)
    if not subscription:
        raise SubscriptionNotFoundException()

    now = datetime.now()

    expired_at = now + relativedelta(months=subscription.months)

    if subscription.free_period_days:
        expired_at += relativedelta(days=subscription.free_period_days)

    return await user_service.update_user(
        user_id=user.id,
        user_data={
            "subscription_acquisition": now,
            "subscription_expired": expired_at,
            "subscription_type": sub_id,
        },
    )
