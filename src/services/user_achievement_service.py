from typing import Dict, List, Union
from src.database.models import User, UserAchievement, Achievement
from src.schemes.achievement_schemas import (
    AchievementCreate,
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

        words = UserAchievementsCategory(title="Слова", achievements=[])

        audio = UserAchievementsCategory(title="Запись", achievements=[])

        video = UserAchievementsCategory(title="Видео", achievements=[])

        for user_achievement in user_achievements:
            if user_achievement.achievement.category == "learned_words":
                words.achievements.append(user_achievement)
            elif user_achievement.achievement.category == "speech_seconds":
                audio.achievements.append(user_achievement)
            elif user_achievement.achievement.category == "video_seconds":
                video.achievements.append(user_achievement)
            elif user_achievement.achievement.category == "added_words":
                words.achievements.append(user_achievement)

        return [words, audio, video]

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
