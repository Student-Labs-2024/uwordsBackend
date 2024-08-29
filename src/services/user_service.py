from typing import List, Union
from datetime import datetime
import uuid
from dateutil.parser import parse
from fastapi import HTTPException, status

from src.config.instance import (
    ACHIEVEMENT_AUDIO,
    ACHIEVEMENT_LEARNED,
    ACHIEVEMENT_VIDEO,
    ACHIEVEMENT_WORDS,
    METRIC_URL,
)
from src.database.models import Achievement, User, UserAchievement
from src.schemes.achievement_schemas import UserAchievementCreate
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
from src.services.achievement_service import AchievementService
from src.services.user_achievement_service import UserAchievementService
from src.utils import password as password_utils
from src.utils import tokens as token_utils
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils.exceptions import (
    AdminNotFoundException,
    IncorrectPasswordException,
    UserEmailNotFoundException,
    UserNotFoundException,
    UserWithGoogleNotFoundException,
    UserWithVkNotFoundException,
)
from src.utils.metric import get_user_data
from src.utils.repository import AbstractRepository
from src.utils.logger import user_service_logger


class UserService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        try:
            return await self.repo.get_one(filters=[User.id == user_id])

        except Exception as e:
            user_service_logger.error(f"[GET USER by ID] Error: {e}")
            return None

    async def get_user_by_uwords_uid(self, uwords_uid: str) -> Union[User, None]:
        try:
            return await self.repo.get_one(filters=[User.uwords_uid == uwords_uid])

        except Exception as e:
            user_service_logger.error(f"[GET USER by UWORDS UID] Error: {e}")
            return None

    async def get_users_with_sub(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(
                filters=[User.subscription_type != None]
            )
        except Exception as e:
            user_service_logger.error(f"[GET USER with SUB] Error: {e}")
            return None

    async def get_users_without_sub(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(
                filters=[User.subscription_type == None]
            )
        except Exception as e:
            user_service_logger.error(f"[GET USER without SUB] Error: {e}")
            return None

    async def get_users(self) -> List[User]:
        try:
            return await self.repo.get_all_by_filter(
                filters=[User.is_active == True], order=User.id.asc()
            )
        except Exception as e:
            user_service_logger.error(f"[GET USERS] Error: {e}")
            return None

    async def get_user_by_provider(
        self, unique: str, provider: str, user_field
    ) -> Union[User, None]:
        try:
            return await self.repo.get_one(
                [user_field == unique, User.provider == provider]
            )
        except Exception as e:
            user_service_logger.error(f"[GET USER by EMAIL] Error: {e}")
            return None

    async def create_user(
        self,
        data: Union[UserCreateVk, UserCreateEmail, UserCreateGoogle],
        provider: str,
        uid: str = None,
    ) -> Union[User, None]:
        try:
            user_data_db = data.model_dump()
            uwords_uid = str(uuid.uuid4())
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
                        uwords_uid=uwords_uid,
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
                        uwords_uid=uwords_uid,
                        provider=provider,
                        birth_date=birth_date,
                        hashed_password=hashed_password.decode(),
                        is_superuser=True,
                        **user_data_db,
                    )
                case Providers.vk.value:
                    user_data_db = UserCreateDB(
                        uwords_uid=uwords_uid,
                        birth_date=birth_date,
                        vk_id=uid,
                        provider=provider,
                        **user_data_db,
                    )
                case Providers.google.value:
                    user_data_db = UserCreateDB(
                        uwords_uid=uwords_uid,
                        birth_date=birth_date,
                        google_id=uid,
                        provider=provider,
                    )
            return await self.repo.add_one(data=user_data_db.model_dump())
        except Exception as e:
            user_service_logger.error(f"[CREATE USER] Error: {e}")
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
                    raise UserEmailNotFoundException(email=login_data.email)
                hashed_password: str = user.hashed_password
                if not password_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise IncorrectPasswordException()
            case Providers.admin.value:
                user = await self.get_user_by_provider(
                    unique=login_data.email,
                    provider=Providers.admin.value,
                    user_field=User.email,
                )
                if not user:
                    raise AdminNotFoundException(email=login_data.email)
                hashed_password: str = user.hashed_password
                if not password_utils.validate_password(
                    password=login_data.password,
                    hashed_password=hashed_password.encode(),
                ):
                    raise IncorrectPasswordException()
            case Providers.vk.value:
                user = await self.get_user_by_provider(
                    unique=uid, provider=Providers.vk.value, user_field=User.vk_id
                )
                if not user:
                    raise UserWithVkNotFoundException(uid=uid)
            case Providers.google.value:
                user = await self.get_user_by_provider(
                    unique=uid,
                    provider=Providers.google.value,
                    user_field=User.google_id,
                )
                if not user:
                    raise UserWithGoogleNotFoundException(uid=uid)
        access_token = token_utils.create_access_token(user=user)
        refresh_token = token_utils.create_refresh_token(user=user)

        return TokenInfo(access_token=access_token, refresh_token=refresh_token)

    async def update_user(self, user_id: int, user_data: dict) -> Union[User, None]:
        try:
            return await self.repo.update_one(
                filters=[User.id == user_id], values=user_data
            )
        except Exception as e:
            user_service_logger.error(f"[UPDATE USER] Error: {e}")
            return None

    async def ban_user(self, user_id: int) -> Union[User, None]:
        try:
            return await self.repo.update_one(
                filters=[User.id == user_id], values={"is_active": False}
            )
        except Exception as e:
            user_service_logger.error(f"[BAN USER] Error: {e}")
            return None

    async def delete_user(self, user_id: int) -> None:
        try:
            return await self.repo.delete_one(filters=[User.id == user_id])
        except Exception as e:
            user_service_logger.error(f"[DELETE USER] Error: {e}")
            return None

    async def update_learning_days(self, uid):
        user = await self.get_user_by_id(uid)
        now = datetime.now()

        today = datetime(now.year, now.month, now.day)

        if user.latest_study:
            if user.latest_study >= today:
                days = 0
            else:
                days = 1

        else:
            days = 1

        try:
            user_days_delta = (
                datetime.date(datetime.now()) - user.latest_study.date()
            ).days
        except:
            user_days_delta = None
        if not user_days_delta or (user_days_delta == 1):
            await self.update_user(
                user.id, {"latest_study": datetime.now(), "days": user.days + days}
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

    async def check_user_achievemets(
        self,
        user_id: int,
        user_achievement_service: UserAchievementService,
    ):
        user = await self.get_user_by_id(user_id=user_id)

        achievement_service = achievement_service_fabric()
        achievements = await achievement_service.get_all()

        for achievement in achievements:
            if await user_achievement_service.get_one_by_achievement_id(
                user_id=user_id, achievement_id=achievement.id
            ):
                continue

            user_achievemets_data = UserAchievementCreate(
                user_id=user_id, achievement_id=achievement.id
            )

            await user_achievement_service.add_one(
                user_achievement=user_achievemets_data.model_dump()
            )

        user_achievements = await user_achievement_service.get_user_achievements(
            user_id=user_id
        )

        try:
            metric = await get_user_data(
                uwords_uid=user.uwords_uid, server_url=METRIC_URL
            )

            for user_achievement in user_achievements:
                progress = user_achievement.progress

                if user_achievement.achievement.category == ACHIEVEMENT_WORDS:
                    progress = metric["alltime_userwords_amount"]
                elif user_achievement.achievement.category == ACHIEVEMENT_LEARNED:
                    progress = metric["alltime_learned_amount"]
                elif user_achievement.achievement.category == ACHIEVEMENT_AUDIO:
                    progress = metric["alltime_speech_seconds"]
                elif user_achievement.achievement.category == ACHIEVEMENT_VIDEO:
                    progress = metric["alltime_video_seconds"]

                if user_achievement.progress >= user_achievement.achievement.target:
                    await user_achievement_service.update_one(
                        user_achievement_id=user_achievement.id,
                        update_data={
                            "is_completed": True,
                            "progress": user_achievement.achievement.target,
                            "progress_percent": 100,
                        },
                    )

                else:
                    await user_achievement_service.update_one(
                        user_achievement_id=user_achievement.id,
                        update_data={
                            "is_completed": False,
                            "progress": progress,
                            "progress_percent": round(
                                (progress / user_achievement.achievement.target) * 100
                            ),
                        },
                    )

        except Exception as e:
            user_service_logger.error(f"[ACHIEVEMENT USER] Error: {e}")

    async def update_onboarding_complete(self, user_id: int) -> User:
        user = await self.repo.get_one([User.id == user_id])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.is_onboarding_complete = True
        return await self.repo.update_one(
            filters=[User.id == user_id], values={"is_onboarding_complete": True}
        )
