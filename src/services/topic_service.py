from src.schemes.schemas import Topic, SubTopic
from src.utils.repository import AbstractRepository


class TopicService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add(self, topic: Topic | SubTopic):
        await self.repo.add_one(dict(topic))

    async def get(self, title) -> Topic | SubTopic:
        return await self.repo.get_one(title)

    async def get_all(self):
        return await self.repo.get_all_by_filter()

    async def check_word(self, word: str) -> str:
        res = await self.repo.update_one(word, 1)
        return res['documents'][0][0]
