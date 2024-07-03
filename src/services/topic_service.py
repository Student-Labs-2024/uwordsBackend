from src.schemes.schemas import Topic
from src.utils.repository import AbstractRepository


class TopicService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_topic(self, topic: Topic):
        topic_dict = {'id': topic.id, 'title': topic.title}
        await self.repo.add_one(topic_dict)

    async def get_topic(self, topic_id: str) -> Topic:
        res = await self.repo.get_one(topic_id)
        return Topic(id=int(res['ids'][0]), title=res['documents'][0])

    async def check_word(self, word: str) -> str:
        res = await self.repo.update_one(word, 1)
        return res['documents'][0][0]
