import logging
from typing import Annotated
from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, status, Depends
from src.config import fastapi_docs_config as doc_data
from src.database.models import User
from src.services.user_service import UserService
from src.services.email_service import EmailService
from src.schemes.schemas import (
    CustomResponse,
    TokenInfo,
    UserCreateEmail,
    UserDump,
    UserUpdate,
    UserCreateVk,
    UserEmailLogin,
    UserCreateGoogle,
    UserGoogleLogin,
)
from src.utils import auth as auth_utils
from src.utils import tokens as token_utils
from src.utils.auth import Providers
from src.utils.dependenes.user_service_fabric import user_service_fabric

logger = logging.getLogger("[ROUTER AUTH]")
logging.basicConfig(level=logging.INFO)

http_bearer = HTTPBearer()
auth_router_v1 = APIRouter(prefix="/api/users", tags=["Users"])


@auth_router_v1.post(
    "/register",
    response_model=UserDump,
    name=doc_data.USER_REGISTER_TITLE,
    description=doc_data.USER_REGISTER_DESCRIPTION,
)
async def register_user(
    user_data: UserCreateEmail,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    if await user_service.get_user_by_provider(
        unique=user_data.email, provider=Providers.email.value
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"User with email {user_data.email} already exists"},
        )
    if not EmailService.check_code(user_data.email, user_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"Wrong code for {user_data.email}"},
        )
    user = await user_service.create_user(
        data=user_data, provider=Providers.email.value
    )
    return user


@auth_router_v1.post(
    "/register/vk",
    response_model=UserDump,
    name=doc_data.USER_REGISTER_VK_TITLE,
    description=doc_data.USER_REGISTER_VK_DESCRIPTION,
)
async def register_vk_user(
    user_data: UserCreateVk,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    stat=Depends(auth_utils.validate_vk_token),
):
    if stat["response"]["success"] == 1:
        if await user_service.get_user_by_provider(
            unique=str(stat["response"]["user_id"]), provider=Providers.vk.value
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "msg": f"User with vk id {stat['response']['user_id']} already exists"
                },
            )
        user = await user_service.create_user(
            data=user_data,
            uid=str(stat["response"]["user_id"]),
            provider=Providers.vk.value,
        )
        return user


@auth_router_v1.post(
    "/register/google",
    response_model=UserDump,
    name=doc_data.USER_REGISTER_GOOGLE_TITLE,
    description=doc_data.USER_REGISTER_GOOGLE_DESCRIPTION,
)
async def register_google_user(
    user_data: UserCreateGoogle,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    if await user_service.get_user_by_provider(
        unique=user_data.google_id, provider=Providers.google.value
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": f"User with google id {user_data.google_id} already exists"},
        )
    user = await user_service.create_user(
        data=user_data,
        uid=user_data.google_id,
        provider=Providers.google.value,
    )
    return user


@auth_router_v1.post(
    "/login",
    response_model=TokenInfo,
    name=doc_data.USER_LOGIN_TITLE,
    description=doc_data.USER_LOGIN_DESCRIPTION,
)
async def user_login(
    login_data: UserEmailLogin,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    return await user_service.auth_user(
        provider=Providers.email.value, login_data=login_data
    )


@auth_router_v1.post(
    "/login/vk",
    response_model=TokenInfo,
    name=doc_data.USER_LOGIN_VK_TITLE,
    description=doc_data.USER_LOGIN_VK_DESCRIPTION,
)
async def user_login_vk(
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    stat=Depends(auth_utils.validate_vk_token),
):
    if stat["response"]["success"] == 1:
        return await user_service.auth_user(
            provider=Providers.vk.value, uid=str(stat["response"]["user_id"])
        )


@auth_router_v1.post(
    "/login/google",
    response_model=TokenInfo,
    name=doc_data.USER_LOGIN_GOOGLE_TITLE,
    description=doc_data.USER_LOGIN_GOOGLE_DESCRIPTION,
)
async def user_login_google(
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user_data: UserGoogleLogin,
):
    return await user_service.auth_user(
        provider=Providers.google.value, uid=user_data.google_id
    )


@auth_router_v1.get(
    "/token/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
    name=doc_data.TOKEN_REFRESH_TITLE,
    description=doc_data.TOKEN_REFRESH_DESCRIPTION,
)
async def refresh_token(user: User = Depends(auth_utils.get_current_user_by_refresh)):
    access_token = token_utils.create_access_token(user=user)

    return TokenInfo(access_token=access_token)


@auth_router_v1.get(
    "/me",
    response_model=UserDump,
    name=doc_data.USER_ME_TITLE,
    description=doc_data.USER_ME_DESCRIPTION,
)
async def get_user_me(
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    await user_service.update_user_state(user.id)
    return user


@auth_router_v1.post(
    "/me/update",
    response_model=UserDump,
    name=doc_data.USER_ME_UPDATE_TITLE,
    description=doc_data.USER_ME_UPDATE_DESCRIPTION,
)
async def update_user_me(
    user_data: UserUpdate,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await user_service.update_user(
        user_id=user.id, user_data=user_data.model_dump(exclude_none=True)
    )


@auth_router_v1.delete(
    "/me/delete",
    response_model=CustomResponse,
    name=doc_data.USER_ME_DELETE_TITLE,
    description=doc_data.USER_ME_DELETE_DESCRIPTION,
)
async def delete_user(
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    await user_service.delete_user(user_id=user.id)

    return CustomResponse(
        status_code=200, message=f"User {user.id} deleted succesfully"
    )


@auth_router_v1.get(
    "/{user_id}",
    response_model=UserDump | None,
    name=doc_data.USER_PROFILE_TITLE,
    description=doc_data.USER_PROFILE_DESCRIPTION,
)
async def get_user_profile(
    user_id: int,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    await user_service.update_user_state(user.id)
    return await user_service.get_user_by_id(user_id=user_id)
