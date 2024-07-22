import logging
from typing import Union
from dateutil.parser import parse
from fastapi import HTTPException, status

from src.database.models import User

from src.schemes.schemas import (
    UserCreateDB,
    TokenInfo,
    UserCreateVk,
    UserEmailLogin,
    AdminEmailLogin,
)

from src.utils import auth as auth_utils
from src.utils import tokens as token_utils
from src.utils.repository import AbstractRepository

logger = logging.getLogger("[SERVICES USER]")
logging.basicConfig(level=logging.INFO)


class UserService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        try:
            return await self.repo.get_one(filters=[User.id == user_id])
        except Exception as e:
            logger.info(f"[GET USER by ID] Error: {e}")
            return None

    async def get_user_by_provider(
        self, unique: str, provider: str
    ) -> Union[User, None]:
        try:
            match provider:
                case auth_utils.Providers.email.value:
                    return await self.repo.get_one(
                        [User.email == unique, User.provider == provider]
                    )
                case auth_utils.Providers.vk.value:
                    return await self.repo.get_one(
                        [User.vk_id == unique, User.provider == provider]
                    )
                case auth_utils.Providers.google.value:
                    return await self.repo.get_one(
                        [User.google_id == unique, User.provider == provider]
                    )
                case auth_utils.Providers.admin.value:
                    return await self.repo.get_one(
                        [User.email == unique, User.provider == provider]
                    )
        except Exception as e:
            logger.info(f"[GET USER by EMAIL] Error: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        try:
            return await self.repo.get_one(filters=[User.email == email])
        except Exception as e:
            logger.info(f"[GET USER by EMAIL] Error: {e}")
            return None

    async def create_user(self, data, provider, uid: str = None) -> Union[User, None]:
        try:
            user_data_db = data.model_dump()
            try:
                birth_date = user_data_db.pop("birth_date")
                birth_date = parse(birth_date, fuzzy=False)
            except:
                birth_date = None
            if type(data) is not UserCreateVk:
                hashed_password: bytes = auth_utils.hash_password(
                    password=data.password
                )
                user_data_db = UserCreateDB(
                    provider=provider,
                    birth_date=birth_date,
                    hashed_password=hashed_password.decode(),
                    **user_data_db,
                )
            else:
                user_data_db = UserCreateDB(
                    birth_date=birth_date, vk_id=uid, provider=provider, **user_data_db
                )
            return await self.repo.add_one(data=user_data_db.model_dump())
        except Exception as e:
            logger.info(f"[CREATE USER] Error: {e}")
            return None

    async def auth_user(
        self,
        provider,
        login_data: UserEmailLogin | AdminEmailLogin | None = None,
        uid=None,
    ) -> TokenInfo:
        match provider:
            case auth_utils.Providers.email.value:
                user = await self.get_user_by_provider(
                    unique=login_data.email, provider=auth_utils.Providers.email.value
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "msg": f"User with email {login_data.email} does not exists"
                        },
                    )
                hashed_password: str = user.hashed_password
                if not auth_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"msg": f"Incorrect password"},
                    )
            case auth_utils.Providers.admin.value:
                user = await self.get_user_by_provider(
                    unique=login_data.email, provider=auth_utils.Providers.admin.value
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "msg": f"Admin with email {login_data.email} does not exists"
                        },
                    )
                hashed_password: str = user.hashed_password
                if not auth_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"msg": f"Incorrect password"},
                    )
            case auth_utils.Providers.vk.value:
                user = await self.get_user_by_provider(
                    unique=uid, provider=auth_utils.Providers.vk.value
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"msg": f"User with vk {uid} does not exists"},
                    )

        access_token = token_utils.create_access_token(user=user)
        refresh_token = token_utils.create_refresh_token(user=user)

        return TokenInfo(access_token=access_token, refresh_token=refresh_token)


async def update_user(self, user_id: int, user_data: dict) -> Union[User, None]:
    try:
        return await self.repo.update_one(
            filters=[User.id == user_id], values=user_data
        )
    except Exception as e:
        logger.info(f"[UPDATE USER] Error: {e}")
        return None


async def ban_user(self, user_id: int) -> Union[User, None]:
    try:
        return await self.repo.update_one(
            filters=[User.id == user_id], values={"is_active": False}
        )
    except Exception as e:
        logger.info(f"[BAN USER] Error: {e}")
        return None


async def delete_user(self, user_id: int) -> None:
    try:
        return await self.repo.delete_one(filters=[User.id == user_id])
    except Exception as e:
        logger.info(f"[DELETE USER] Error: {e}")
        return None
