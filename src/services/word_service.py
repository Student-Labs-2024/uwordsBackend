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

    async def get_word(self, enValue: str) -> Word:
        try:
            res = await self.repo.get_one([Word.enValue == enValue,])
            return res

        except BaseException as e:
            logger.info(f'[GET WORD] ERROR: {e}')
            return None

    async def upload_new_word(self, enValue: str, ruValue: str) -> Word | None:
        try:
            if CensoreFilter.is_censore(text=ruValue):
                logger.info(f'[UPLOAD WORD] CENSORE: {ruValue}')
                return None

            audio_link = AudioService.word_to_speech(word=enValue)
            picture_link = AudioService.download_picture(word=enValue)

            word = await self.repo.add_one(
                {'enValue': enValue, 'ruValue': ruValue, 'audioLink': audio_link, 'pictureLink': picture_link})
            return word


        except BaseException as e:
            logger.info(f'[UPLOAD WORD] ERROR: {e}')
