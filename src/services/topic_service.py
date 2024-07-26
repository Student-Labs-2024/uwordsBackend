from typing import Union, Dict, List

from src.database.models import Topic, SubTopic
from src.utils.repository import AbstractRepository


class TopicService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add(self, topic: Dict):
        try:
            await self.repo.add_one(data=topic)
        except Exception:
            return True

    async def get(self, title) -> Union[Topic, SubTopic, None]:
        return await self.repo.get_one(title)

    async def get_all(self) -> Union[List[Topic], List[SubTopic], List]:
        return await self.repo.get_all_by_filter()

    async def delete(self, title):
        return await self.repo.delete_one(title)

    async def check_word(self, word: str) -> str:
        res = await self.repo.update_one(word, 1)
        if res:
            return res["documents"][0][0]
        return ""
