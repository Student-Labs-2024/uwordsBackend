from src.schemes.schemas import Topic, SubTopic
from src.utils.repository import AbstractRepository


class TopicService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add(self, topic: Topic | SubTopic):
        try:
            await self.repo.add_one(dict(topic))
        except:
            return True

    async def get(self, title) -> Topic | SubTopic | None:
        return await self.repo.get_one(title)

    async def get_all(self):
        return await self.repo.get_all_by_filter()

    async def delete(self, title):
        return await self.repo.delete_one(title)

    async def check_word(self, word: str) -> str:
        res = await self.repo.update_one(word, 1)
        if res:
            return res['documents'][0][0]
        return ""
