import logging
from typing import Annotated

from fastapi.security import HTTPBearer
from fastapi import APIRouter, Depends, HTTPException, status

from src.database.models import User
from src.schemes.admin_schemas import AdminCreate, AdminEmailLogin

from src.schemes.enums.enums import Providers
from src.schemes.user_schemas import UserDump
from src.schemes.util_schemas import TokenInfo, CustomResponse

from src.services.user_service import UserService

from src.utils import auth as auth_utils
from src.utils.dependenes.user_service_fabric import user_service_fabric

from src.config.instance import ADMIN_SECRET
from src.config import fastapi_docs_config as doc_data


logger = logging.getLogger("[ROUTER ADMIN]")
logging.basicConfig(level=logging.INFO)

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"Admin with email {admin_data.email} already exists"},
        )

    if not admin_data.admin_secret == ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": f"Incorrect admin-create key"},
        )

    user = await user_service.create_user(
        data=admin_data, provider=Providers.admin.value
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
