from typing import Dict, List, Union
from src.config.instance import (
    ACHIEVEMENT_AUDIO,
    ACHIEVEMENT_LEARNED,
    ACHIEVEMENT_VIDEO,
    ACHIEVEMENT_WORDS,
)
from src.database.models import User, UserAchievement, Achievement
from src.schemes.achievement_schemas import (
    AchievementCreate,
    AchievementDump,
    UserAchievementCreate,
    UserAchievementDump,
    UserAchievementsCategory,
)
from src.utils.repository import AbstractRepository


class UserAchievementService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, user_achievement: Dict):
        return await self.repo.add_one(data=user_achievement)

    async def get(self, title) -> Union[UserAchievement, None]:
        return await self.repo.get_one(title)

    async def get_one_by_achievement_id(
        self, user_id: int, achievement_id: int
    ) -> UserAchievement:
        return await self.repo.get_one(
            filters=[
                UserAchievement.achievement_id == achievement_id,
                UserAchievement.user_id == user_id,
            ]
        )

    async def get_all(self) -> list[UserAchievement]:
        return await self.repo.get_all_by_filter()

    async def update_one(
        self, user_achievement_id: int, update_data: dict
    ) -> UserAchievement:
        return await self.repo.update_one(
            filters=[UserAchievement.id == user_achievement_id], values=update_data
        )

    async def delete_one(self, user_achievement_id: int) -> None:
        await self.repo.delete_one(filters=[UserAchievement.id == user_achievement_id])

    async def get_user_achievements(self, user_id: int) -> list[UserAchievement]:
        return await self.repo.get_all_by_filter(
            [UserAchievement.user_id == user_id], UserAchievement.id.asc()
        )

    async def get_user_achievements_dump(
        self, user_id: int
    ) -> List[UserAchievementsCategory]:
        user_achievements = await self.get_user_achievements(user_id=user_id)

        words, learned, audio, video = [], [], [], []

        for user_achievement in user_achievements:

            user_achievement_dump = UserAchievementDump(
                id=user_achievement.id,
                user_id=user_id,
                progress=user_achievement.progress,
                progress_percent=user_achievement.progress_percent,
                is_completed=user_achievement.is_completed,
                achievement=AchievementDump(
                    id=user_achievement.achievement.id,
                    title=user_achievement.achievement.title,
                    description=user_achievement.achievement.description,
                    pictureLink=(
                        user_achievement.achievement.pictureLinkComplete
                        if user_achievement.is_completed
                        else user_achievement.achievement.pictureLink
                    ),
                    category=user_achievement.achievement.category,
                    stage=user_achievement.achievement.stage,
                    target=user_achievement.achievement.target,
                ),
            )

            if user_achievement.achievement.category == ACHIEVEMENT_WORDS:
                words.append(user_achievement_dump)
            elif user_achievement.achievement.category == ACHIEVEMENT_LEARNED:
                learned.append(user_achievement_dump)
            elif user_achievement.achievement.category == ACHIEVEMENT_AUDIO:
                audio.append(user_achievement_dump)
            elif user_achievement.achievement.category == ACHIEVEMENT_VIDEO:
                video.append(user_achievement_dump)

        words: List[UserAchievementDump] = sorted(
            words, key=lambda x: x.progress_percent, reverse=True
        )
        learned: List[UserAchievementDump] = sorted(
            learned, key=lambda x: x.progress_percent, reverse=True
        )
        audio: List[UserAchievementDump] = sorted(
            audio, key=lambda x: x.progress_percent, reverse=True
        )
        video: List[UserAchievementDump] = sorted(
            video, key=lambda x: x.progress_percent, reverse=True
        )

        return [
            UserAchievementsCategory(title="Словарь", achievements=words),
            UserAchievementsCategory(title="Обучение", achievements=learned),
            UserAchievementsCategory(title="Запись", achievements=audio),
            UserAchievementsCategory(title="Видео", achievements=video),
        ]

    async def update_user_achievements(
        self, users: List[User], achievements: List[Achievement]
    ):

        for achievement in achievements:
            for user in users:
                if not await self.repo.get_one(
                    filters=[
                        UserAchievement.achievement_id == achievement.id,
                        UserAchievement.user_id == user.id,
                    ]
                ):
                    user_achievemets_data = UserAchievementCreate(
                        user_id=user.id, achievement_id=achievement.id
                    )
                    await self.repo.add_one(data=user_achievemets_data.model_dump())
