import logging
from datetime import datetime

from src.config.instance import MINIO_BUCKET_VOICEOVER, MINIO_BUCKET_PICTURE
from src.database import models
from src.schemes.schemas import ErrorCreate
from src.services.error_service import ErrorService
from src.database.models import UserWord, Word
from src.services.censore_service import CensoreFilter
from src.services.minio_uploader import MinioUploader
from src.services.services_config import mc
from src.services.topic_service import TopicService
from src.services.word_service import WordService
from src.utils.repository import AbstractRepository

logger = logging.getLogger("[SERVICES WORDS]")
logging.basicConfig(level=logging.INFO)


class UserWordService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_user_words(self, user_id: str):
        return await self.repo.get_all_by_filter([UserWord.user_id == user_id], UserWord.frequency.desc())

    async def get_user_word(self, user_id: str, word_id: int) -> UserWord:
        try:
            user_word: UserWord = await self.repo.get_one([UserWord.user_id == user_id, UserWord.word_id == word_id])
            return user_word

        except BaseException as e:
            logger.info(f'[GET USER WORD] ERROR: {e}')

    async def get_user_words_for_study(self, user_id: str, topic_title: str, subtopic_title: str | None = None):
        try:
            if not subtopic_title:
                user_words = await self.repo.get_all_by_filter(
                    [UserWord.user_id == user_id, UserWord.word.has(Word.topic == topic_title)],
                    UserWord.progress.desc())
            else:
                user_words = await self.repo.get_all_by_filter(
                    [UserWord.user_id == user_id, UserWord.word.has(Word.topic == topic_title),
                     UserWord.word.has(Word.subtopic == subtopic_title)], UserWord.progress.desc())
            words_for_study = []
            time_now = datetime.now()

            for user_word in user_words:
                if user_word.latest_study:
                    time_delta = time_now - user_word.latest_study
                    seconds = time_delta.seconds
                else:
                    seconds = 86400

                if user_word.progress < 3 and seconds >= 86400 and len(words_for_study) < 4:
                    words_for_study.append(user_word)

            return words_for_study
        except BaseException as e:
            logger.info(f'[GET USER WORDS FOR STUDY] ERROR: {e}')

    async def update_progress_word(self, user_id: str, words_ids: list[int]):
        try:
            time_now = datetime.now()
            learned = 0

            for word_id in words_ids:
                user_word = await self.repo.get_one([UserWord.user_id == user_id, UserWord.id == word_id])
                if user_word.progress < 3:
                    await self.repo.update_one([UserWord.user_id == user_id, UserWord.id == word_id],
                                               {'latest_study': time_now, 'progress': user_word.progress + 1})
                    learned += 1
        except BaseException as e:
            logger.info(f'[UPLOAD USER WORD] ERROR: {e}')

    async def upload_user_word(self, new_word: dict, user_id: str, word_service: WordService,
                               subtopic_service: TopicService, error_service: ErrorService) -> bool:
        try:
            en_value = new_word.get('enValue', None)
            ru_value = new_word.get('ruValue', None)
            frequency = new_word.get('frequency', 0)
            is_new = False

            if CensoreFilter.is_censore(text=ru_value):
                logger.info(f'[UPLOAD WORD] CENSORE: {ru_value}')
                return None

            word = await word_service.get_word(en_value=en_value)

            if not word:
                subtopic_title = await subtopic_service.check_word(en_value)
                subtopic = await subtopic_service.get([models.SubTopic.title == subtopic_title])
                word = await word_service.upload_new_word(en_value=en_value, ru_value=ru_value,
                                                          topic_title=subtopic.topic_title,
                                                          subtopic_title=subtopic_title)
                is_new = True
            user_word = await self.get_user_word(user_id=user_id, word_id=word.id)
            if not user_word:
                await self.repo.add_one({'word_id': word.id, 'user_id': user_id, 'frequency': frequency})
            else:
                user_word_frequency = user_word.frequency + frequency
                await self.repo.update_one([UserWord.user_id == user_id, UserWord.word_id == word.id],
                                           {'frequency': user_word_frequency, })

            return is_new
        except BaseException as e:
            logger.info(f'[UPLOAD USER WORD] ERROR: {e}')
            error = ErrorCreate(
                user_id=user_id,
                message="[CREATE FREQ]",
                description=str(e)
            )
            
            await error_service.add_one(error=error)
            
            return False


    async def upload_user_words(self, user_words: list[dict], user_id: str, word_service: WordService,
                                subtopic_service: TopicService, error_service: ErrorService) -> bool:
        try:
            found_voiceover_bucket = mc.bucket_exists(MINIO_BUCKET_VOICEOVER)
            if not found_voiceover_bucket:
                MinioUploader.create_bucket(MINIO_BUCKET_VOICEOVER)

            found_picture_bucket = mc.bucket_exists(MINIO_BUCKET_PICTURE)
            if not found_picture_bucket:
                MinioUploader.create_bucket(MINIO_BUCKET_PICTURE)

            new_words = 0
            all_words = len(user_words)

            for user_word in user_words:
                is_new = await self.upload_user_word(user_word, user_id, word_service, subtopic_service, error_service)
                if is_new:
                    new_words += 1

            return True

        except BaseException as e:
            logger.info(f'[UPLOAD USER WORDS] ERROR: {e}')
            error = ErrorCreate(
                user_id=user_id,
                message="[CREATE FREQ]",
                description=str(e)
            )

            await error_service.add_one(error=error)

            return None
