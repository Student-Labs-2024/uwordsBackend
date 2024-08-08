import logging
from typing import Annotated
from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, status, Depends

from src.config.instance import METRIC_URL
from src.database.models import User

from src.config import fastapi_docs_config as doc_data
from src.schemes.feedback_schemas import FeedbackDump, FeedbackCreate, FeedbackUpdate
from src.schemes.user_schemas import (
    UserDump,
    UserCreateEmail,
    UserCreateVk,
    UserCreateGoogle,
    UserEmailLogin,
    UserGoogleLogin,
    UserUpdate,
)
from src.schemes.util_schemas import TokenInfo, CustomResponse

from src.services.achievement_service import AchievementService
from src.services.feedback_service import FeedbackService
from src.services.user_service import UserService
from src.services.email_service import EmailService

from src.schemes.enums.enums import Providers

from src.utils import auth as auth_utils
from src.utils import tokens as token_utils
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils.metric import get_user_data
from src.utils.dependenes.feedback_service_fabric import feedback_service_fabric
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
        unique=user_data.email, provider=Providers.email.value, user_field=User.email
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
            unique=str(stat["response"]["user_id"]),
            provider=Providers.vk.value,
            user_field=User.vk_id,
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
        unique=user_data.google_id,
        provider=Providers.google.value,
        user_field=User.google_id,
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
    achievements_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_active_current_user),
):
    additional_data = await get_user_data(user.id, METRIC_URL)

    if additional_data:
        user.metrics = additional_data

    user_achivements = await achievements_service.get_user_achievements(user.id)

    achievements_data = await user_service.check_user_achivemets(
        user.id, user_achivements
    )

    if achievements_data:
        user.achievements = achievements_data

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


@auth_router_v1.post(
    "/feedback",
    response_model=FeedbackDump,
    name=doc_data.FEEDBACK_TITLE,
    description=doc_data.FEEDBACK_DESCRIPTION,
)
async def create_feedback(
    feedback_data: FeedbackCreate,
    feedback_service: Annotated[FeedbackService, Depends(feedback_service_fabric)],
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if await feedback_service.user_has_feedback(user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "User has already submitted a feedback"},
        )
    if feedback_data.stars < 1 or feedback_data.stars > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Stars must be between 1 and 5"},
        )

    feedback = await feedback_service.add_one(user_id=user.id, feedback=feedback_data)
    return feedback


@auth_router_v1.post(
    "/feedback/update",
    response_model=FeedbackDump,
    name=doc_data.FEEDBACK_UPDATE_TITLE,
    description=doc_data.FEEDBACK_UPDATE_DESCRIPTION,
)
async def update_feedback(
    feedback_data: FeedbackUpdate,
    feedback_service: Annotated[FeedbackService, Depends(feedback_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if not await feedback_service.user_has_feedback(user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "User has not submitted a feedback yet"},
        )
    if feedback_data.stars < 1 or feedback_data.stars > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Stars must be between 1 and 5"},
        )

    existing_feedback = await feedback_service.get_user_feedback(user.id)
    feedback_id = existing_feedback[0].id

    updated_feedback = await feedback_service.update_feedback(
        feedback_id, feedback_data.model_dump()
    )
    return updated_feedback
