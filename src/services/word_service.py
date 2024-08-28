import logging
from typing import Union

from src.database.models import Word

from src.utils.repository import AbstractRepository

from src.services.audio_service import AudioService
from src.services.image_service import ImageDownloader
from src.utils.logger import word_service_logger


class WordService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_word(self, en_value: str) -> Union[Word, None]:
        try:
            res = await self.repo.get_one(
                [
                    Word.enValue == en_value,
                ]
            )
            return res

        except BaseException as e:
            word_service_logger.error(f"[GET WORD] ERROR: {e}")
            return None

    async def upload_new_word(
        self, en_value: str, ru_value: str, topic_title: str, subtopic_title: str
    ) -> Union[Word, None]:
        try:
            picture_link = await ImageDownloader.download_picture(word=en_value)

            if not picture_link:
                return None

            audio_link = await AudioService.word_to_speech(word=en_value)

            word = await self.repo.add_one(
                {
                    "enValue": en_value,
                    "ruValue": ru_value,
                    "audioLink": audio_link,
                    "pictureLink": picture_link,
                    "topic": topic_title,
                    "subtopic": subtopic_title,
                }
            )
            return word

        except BaseException as e:
            word_service_logger.error(f"[UPLOAD WORD] ERROR: {e}")
            return None
