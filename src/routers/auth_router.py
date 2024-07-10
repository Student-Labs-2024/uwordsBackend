import logging
from typing import Annotated

from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, status, Depends

from src.database.models import User
from src.services.user_service import UserService
from src.schemes.schemas import TokenInfo, UserCreate, UserCreateDB, UserDump, UserLogin, UserUpdate

from src.utils import auth as auth_utils
from src.utils import tokens as token_utils
from src.utils.dependenes.user_service_fabric import user_service_fabric


logger = logging.getLogger("[ROUTER AUTH]")
logging.basicConfig(level=logging.INFO)

http_bearer = HTTPBearer()
auth_router_v1 = APIRouter(prefix="/api/users", tags=["Users"])


@auth_router_v1.post("/register", response_model=UserDump)
async def register_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(user_service_fabric)]
):
    
    if await user_service.get_user_by_email_provider(email=user_data.email, provider=user_data.provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"User {user_data.provider} with email {user_data.email} already exists"
            }
        )
    
    hashed_password: bytes = auth_utils.hash_password(password=user_data.password)

    user_data_db = UserCreateDB(
        hashed_password=hashed_password.decode(),
        **user_data.model_dump()
    )

    user = await user_service.create_user(
        user_data=user_data_db.model_dump()
    )

    return user


@auth_router_v1.post("/login", response_model=TokenInfo)
async def user_login(
    login_data: UserLogin,
    user_service: Annotated[UserService, Depends(user_service_fabric)]
):
    
    user = await user_service.get_user_by_email_provider(email=login_data.email, provider=login_data.provider)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": f"User {login_data.provider} with email {login_data.email} does not exists"
            }
        )
    
    hashed_password: str = user.hashed_password
    
    if not auth_utils.validate_password(
        password=login_data.password,
        hashed_password=hashed_password.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Incorrect password"
            }
        )
    
    access_token = token_utils.create_access_token(user=user)
    refresh_token = token_utils.create_refresh_token(user=user)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )


@auth_router_v1.get("/token/refresh", response_model=TokenInfo, response_model_exclude_none=True)
async def refresh_token(
    user: User = Depends(auth_utils.get_current_user_by_refresh)
):
    access_token = token_utils.create_access_token(user=user)
    
    return TokenInfo(
        access_token=access_token
    )


@auth_router_v1.get("/me", response_model=UserDump)
async def get_user_me(
    user: User = Depends(auth_utils.get_active_current_user)
):
    return user


@auth_router_v1.post("/me/update", response_model=UserDump)
async def update_user_me(
    user_data: UserUpdate,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await user_service.update_user(user_id=user.id, user_data=user_data.model_dump())