import logging
from src.database.models import Word
from src.services.audio_service import AudioService
from src.services.censore_service import CensoreFilter
from src.utils.repository import AbstractRepository

logger = logging.getLogger("[SERVICES WORDS]")
logging.basicConfig(level=logging.INFO)


class WordService:

    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_word(self, en_value: str) -> Word | None:
        try:
            res = await self.repo.get_one([Word.enValue == en_value, ])
            return res

        except BaseException as e:
            logger.info(f'[GET WORD] ERROR: {e}')
            return None

    async def upload_new_word(self, en_value: str, ru_value: str, topic_title: str, subtopic_title: str) -> Word | None:
        try:
            audio_link = AudioService.word_to_speech(word=en_value)
            picture_link = AudioService.download_picture(word=en_value)

            word = await self.repo.add_one(
                {'enValue': en_value, 'ruValue': ru_value, 'audioLink': audio_link, 'pictureLink': picture_link,
                 'topic': topic_title, 'subtopic': subtopic_title})
            return word


        except BaseException as e:
            logger.info(f'[UPLOAD WORD] ERROR: {e}')
