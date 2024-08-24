import logging
from typing import Dict, Union

from src.database.models import UserWordStopList
from src.utils.repository import AbstractRepository


logger = logging.getLogger("[SERVICES USER WORD STOP LIST]")

logging.basicConfig(level=logging.INFO)


class UserWordStopListService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, user_word_stop_data: Dict) -> UserWordStopList:
        return await self.repo.add_one(data=user_word_stop_data)

    async def get_user_word_stop(
        self, user_id: int, word_id: int
    ) -> Union[UserWordStopList, None]:
        try:
            user_word_stop: UserWordStopList = await self.repo.get_one(
                [
                    UserWordStopList.user_id == user_id,
                    UserWordStopList.word_id == word_id,
                ]
            )
            return user_word_stop

        except BaseException as e:
            logger.info(f"[GET USER WORD] ERROR: {e}")
            return None

    async def delete_one(self, user_word_stop_id: int) -> None:
        await self.repo.delete_one(filters=[UserWordStopList.id == user_word_stop_id])
