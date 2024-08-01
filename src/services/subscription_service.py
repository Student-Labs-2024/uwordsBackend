from src.database import models
from src.schemes.schemas import Subscription
from src.utils.repository import AbstractRepository


class SubscriptionService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_sub(self, sub: Subscription):
        return await self.repo.add_one(data=sub.model_dump())

    async def get_sub(self, name: str):
        return await self.repo.get_one([models.Subscription.name == name])

    async def get_sub_by_id(self, id: int) -> Subscription:
        return await self.repo.get_one([models.Subscription.id == id])

    async def update_sub(self, name: str, data):
        return await self.repo.update_one([models.Subscription.name == name], data)

    async def delete_sub(self, name: str):
        await self.repo.delete_one([models.Subscription.name == name])
