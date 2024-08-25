from typing import Dict, Union
from src.database.models import Achievement, UserAchievement
from src.utils.repository import AbstractRepository


class AchievementService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, achievement: Dict):
        return await self.repo.add_one(data=achievement)

    async def get(self, title) -> Union[Achievement, None]:
        return await self.repo.get_one(title)

    async def get_all(self) -> list[Achievement]:
        return await self.repo.get_all_by_filter()

    async def update_one(self, achievement_id: int, update_data: dict) -> Achievement:
        return await self.repo.update_one(
            filters=[Achievement.id == achievement_id], values=update_data
        )

    async def delete_one(self, achievement_id: int) -> None:
        await self.repo.delete_one(filters=[Achievement.id == achievement_id])

    async def get_user_achievements(self, user_id: int) -> list[UserAchievement]:
        return await self.repo.get_all_by_filter(
            [UserAchievement.user_id == user_id], UserAchievement.id.desc()
        )
