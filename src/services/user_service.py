import logging
from typing import List, Union
from datetime import datetime
from dateutil.parser import parse
from fastapi import HTTPException, status

from src.database.models import User
from src.schemes.admin_schemas import AdminEmailLogin

from src.schemes.enums.enums import Providers
from src.schemes.user_schemas import (
    UserCreateVk,
    UserCreateEmail,
    UserCreateGoogle,
    UserCreateDB,
    UserEmailLogin,
)
from src.schemes.util_schemas import TokenInfo

from src.utils import password as password_utils
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

    async def get_users_with_sub(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(
                filters=[User.subscription_type != None]
            )
        except Exception as e:
            logger.info(f"[GET USER with SUB] Error: {e}")
            return None

    async def get_users_without_sub(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(
                filters=[User.subscription_type == None]
            )
        except Exception as e:
            logger.info(f"[GET USER without SUB] Error: {e}")
            return None

    async def get_users(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(filters=None)
        except Exception as e:
            logger.info(f"[GET USERS] Error: {e}")
            return None

    async def get_user_by_provider(
        self, unique: str, provider: str, user_field
    ) -> Union[User, None]:
        try:
            return await self.repo.get_one(
                [user_field == unique, User.provider == provider]
            )
        except Exception as e:
            logger.info(f"[GET USER by EMAIL] Error: {e}")
            return None

    async def create_user(
        self,
        data: Union[UserCreateVk, UserCreateEmail, UserCreateGoogle],
        provider: str,
        uid: str = None,
    ) -> Union[User, None]:
        try:
            user_data_db = data.model_dump()
            try:
                birth_date = user_data_db.pop("birth_date")
                birth_date = parse(birth_date, fuzzy=False)
            except:
                birth_date = None
            match provider:
                case Providers.email.value:
                    hashed_password: bytes = password_utils.hash_password(
                        password=data.password
                    )
                    user_data_db = UserCreateDB(
                        provider=provider,
                        birth_date=birth_date,
                        hashed_password=hashed_password.decode(),
                        **user_data_db,
                    )
                case Providers.admin.value:
                    hashed_password: bytes = password_utils.hash_password(
                        password=data.password
                    )
                    user_data_db = UserCreateDB(
                        provider=provider,
                        birth_date=birth_date,
                        hashed_password=hashed_password.decode(),
                        is_superuser=True,
                        **user_data_db,
                    )
                case Providers.vk.value:
                    user_data_db = UserCreateDB(
                        birth_date=birth_date,
                        vk_id=uid,
                        provider=provider,
                        **user_data_db,
                    )
                case Providers.google.value:
                    user_data_db = UserCreateDB(
                        birth_date=birth_date, google_id=uid, provider=provider
                    )
            return await self.repo.add_one(data=user_data_db.model_dump())
        except Exception as e:
            logger.info(f"[CREATE USER] Error: {e}")
            return None

    async def auth_user(
        self,
        provider: str,
        login_data: Union[UserEmailLogin, AdminEmailLogin, None] = None,
        uid=None,
    ) -> TokenInfo:
        match provider:
            case Providers.email.value:
                user = await self.get_user_by_provider(
                    unique=login_data.email,
                    provider=Providers.email.value,
                    user_field=User.email,
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "msg": f"User with email {login_data.email} does not exists"
                        },
                    )
                hashed_password: str = user.hashed_password
                if not password_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"msg": f"Incorrect password"},
                    )
            case Providers.admin.value:
                user = await self.get_user_by_provider(
                    unique=login_data.email,
                    provider=Providers.admin.value,
                    user_field=User.email,
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "msg": f"Admin with email {login_data.email} does not exists"
                        },
                    )
                hashed_password: str = user.hashed_password
                if not password_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"msg": f"Incorrect password"},
                    )
            case Providers.vk.value:
                user = await self.get_user_by_provider(
                    unique=uid, provider=Providers.vk.value, user_field=User.vk_id
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"msg": f"User with vk {uid} does not exists"},
                    )
            case Providers.google.value:
                user = await self.get_user_by_provider(
                    unique=uid,
                    provider=Providers.google.value,
                    user_field=User.google_id,
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"msg": f"User with google {uid} does not exists"},
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

    async def update_learning_days(self, uid):
        user = await self.get_user_by_id(uid)
        try:
            user_days_delta = (
                datetime.date(datetime.now()) - user.latest_study.date()
            ).days
        except:
            user_days_delta = None
        if not user_days_delta or (user_days_delta == 1):
            await self.update_user(
                user.id, {"latest_study": datetime.now(), "days": user.days + 1}
            )
        if user_days_delta and user_days_delta >= 2:
            await self.update_user(user.id, {"latest_study": datetime.now(), "days": 1})

    async def update_user_state(self, uid):
        user = await self.get_user_by_id(uid)
        try:
            user_days_delta = (
                datetime.date(datetime.now()) - user.latest_study.date()
            ).days
        except:
            user_days_delta = None
        if user_days_delta and user_days_delta >= 2:
            await self.update_user(user.id, {"latest_study": datetime.now(), "days": 1})
