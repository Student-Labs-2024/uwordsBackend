import logging
from typing import Union, List, Dict
from datetime import datetime, timedelta

from src.schemes.error_schemas import ErrorCreate
from src.utils.metric import send_user_data
from src.utils.repository import AbstractRepository
from src.database.models import UserWord, Word, SubTopic

from src.services.services_config import mc
from src.services.word_service import WordService
from src.services.error_service import ErrorService
from src.services.topic_service import TopicService
from src.services.minio_uploader import MinioUploader
from src.services.censore_service import CensoreFilter

from src.config.instance import (
    METRIC_URL,
    STUDY_DELAY,
    STUDY_MAX_PROGRESS,
    STUDY_WORDS_AMOUNT,
    MINIO_BUCKET_PICTURE,
    MINIO_BUCKET_VOICEOVER,
    MINIO_BUCKET_PICTURE_RACY,
    MINIO_BUCKET_PICTURE_ADULT,
    MINIO_BUCKET_PICTURE_MEDICAL,
    MINIO_BUCKET_PICTURE_VIOLENCE,
)


logger = logging.getLogger("[SERVICES WORDS]")

logging.basicConfig(level=logging.INFO)


class UserWordService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_user_words(self, user_id: int) -> List[UserWord]:
        return await self.repo.get_all_by_filter(
            [UserWord.user_id == user_id], UserWord.frequency.desc()
        )

    async def get_user_words_by_filter(
        self, user_id: int, topic_title: str, subtopic_title: Union[str, None] = None
    ) -> Union[List[UserWord], List]:
        try:
            if not subtopic_title:
                return await self.repo.get_all_by_filter(
                    filters=[
                        UserWord.user_id == user_id,
                        UserWord.word.has(Word.topic == topic_title),
                    ]
                )

            return await self.repo.get_all_by_filter(
                filters=[
                    UserWord.user_id == user_id,
                    UserWord.word.has(Word.topic == topic_title),
                    UserWord.word.has(Word.subtopic == subtopic_title),
                ]
            )

        except Exception as e:
            logger.info(f"[GET USER WORDS By FILTER] ERROR: {e}")
            return []

    async def get_user_word(self, user_id: int, word_id: int) -> Union[UserWord, None]:
        try:
            user_word: UserWord = await self.repo.get_one(
                [UserWord.user_id == user_id, UserWord.word_id == word_id]
            )
            return user_word

        except BaseException as e:
            logger.info(f"[GET USER WORD] ERROR: {e}")
            return None

    async def get_user_words_for_study(
        self, user_id: int, topic_title: str, subtopic_title: Union[str, None] = None
    ) -> Union[List[UserWord], List]:
        try:
            if not subtopic_title:
                user_words: List[UserWord] = await self.repo.get_all_by_filter(
                    [
                        UserWord.user_id == user_id,
                        UserWord.word.has(Word.topic == topic_title),
                    ],
                    UserWord.progress.desc(),
                )
            else:
                user_words: List[UserWord] = await self.repo.get_all_by_filter(
                    [
                        UserWord.user_id == user_id,
                        UserWord.word.has(Word.topic == topic_title),
                        UserWord.word.has(Word.subtopic == subtopic_title),
                    ],
                    UserWord.progress.desc(),
                )
            words_for_study = []
            time_now = datetime.now()

            for user_word in user_words:
                if user_word.latest_study:
                    time_delta: timedelta = time_now - user_word.latest_study
                    seconds = time_delta.seconds
                else:
                    seconds = STUDY_DELAY

                if (
                    user_word.progress < STUDY_MAX_PROGRESS
                    and seconds >= STUDY_DELAY
                    and len(words_for_study) < STUDY_WORDS_AMOUNT
                ):
                    words_for_study.append(user_word)

            return words_for_study
        except BaseException as e:
            logger.info(f"[GET USER WORDS FOR STUDY] ERROR: {e}")
            return []

    async def update_progress_word(self, user_id: int, words_ids: List[int]) -> None:
        try:
            time_now = datetime.now()
            learned = 0

            for word_id in words_ids:
                user_word = await self.repo.get_one(
                    [UserWord.user_id == user_id, UserWord.id == word_id]
                )
                if user_word.progress < STUDY_MAX_PROGRESS:
                    upd_user_word = await self.repo.update_one(
                        [UserWord.user_id == user_id, UserWord.id == word_id],
                        {"latest_study": time_now, "progress": user_word.progress + 1},
                    )
                    if upd_user_word.progress == STUDY_MAX_PROGRESS:
                        learned += 1

            data = {"user_id": user_id, "learned_amount": learned}

            await send_user_data(data=data, server_url=METRIC_URL)

        except BaseException as e:
            logger.info(f"[UPLOAD USER WORD] ERROR: {e}")

    async def upload_user_word(
        self,
        new_word: Dict,
        user_id: int,
        word_service: WordService,
        subtopic_service: TopicService,
        error_service: ErrorService,
    ) -> bool:
        try:
            en_value = new_word.get("enValue", None)
            ru_value = new_word.get("ruValue", None)
            frequency = new_word.get("frequency", 0)
            is_new = False

            if CensoreFilter.is_censore(text=ru_value):
                logger.info(f"[UPLOAD WORD] CENSORE: {ru_value}")
                return None

            if CensoreFilter.is_censore(text=en_value):
                logger.info(f"[UPLOAD WORD] CENSORE: {en_value}")
                return None

            word = await word_service.get_word(en_value=en_value)
            if not word:
                subtopic_title = await subtopic_service.check_word(en_value)
                subtopic = await subtopic_service.get(
                    [SubTopic.title == subtopic_title]
                )
                word = await word_service.upload_new_word(
                    en_value=en_value,
                    ru_value=ru_value,
                    topic_title=subtopic.topic_title,
                    subtopic_title=subtopic_title,
                )

                if not word:
                    return False

                is_new = True
            user_word = await self.get_user_word(user_id=user_id, word_id=word.id)
            if not user_word:
                await self.repo.add_one(
                    {"word_id": word.id, "user_id": user_id, "frequency": frequency}
                )
            else:
                user_word_frequency = user_word.frequency + frequency
                await self.repo.update_one(
                    [UserWord.user_id == user_id, UserWord.word_id == word.id],
                    {
                        "frequency": user_word_frequency,
                    },
                )

            return is_new
        except BaseException as e:
            logger.info(f"[UPLOAD USER WORD] ERROR: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return False

    async def upload_user_words(
        self,
        user_words: List[Dict],
        user_id: int,
        word_service: WordService,
        subtopic_service: TopicService,
        error_service: ErrorService,
    ) -> bool:
        try:
            found_voiceover_bucket = mc.bucket_exists(MINIO_BUCKET_VOICEOVER)
            if not found_voiceover_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_VOICEOVER)

            found_picture_bucket = mc.bucket_exists(MINIO_BUCKET_PICTURE)
            if not found_picture_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_PICTURE)

            found_picture_adult_bucket = mc.bucket_exists(MINIO_BUCKET_PICTURE_ADULT)
            if not found_picture_adult_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_PICTURE_ADULT)

            found_picture_medical_bucket = mc.bucket_exists(
                MINIO_BUCKET_PICTURE_MEDICAL
            )
            if not found_picture_medical_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_PICTURE_MEDICAL)

            found_picture_violence_bucket = mc.bucket_exists(
                MINIO_BUCKET_PICTURE_VIOLENCE
            )
            if not found_picture_violence_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_PICTURE_VIOLENCE)

            found_picture_racy_bucket = mc.bucket_exists(MINIO_BUCKET_PICTURE_RACY)
            if not found_picture_racy_bucket:
                await MinioUploader.create_bucket(MINIO_BUCKET_PICTURE_RACY)

            add_words_amount = 0
            add_userwords_amount = len(user_words)

            for user_word in user_words:
                is_new = await self.upload_user_word(
                    user_word, user_id, word_service, subtopic_service, error_service
                )
                if is_new:
                    add_words_amount += 1

            data = {
                "user_id": user_id,
                "add_words_amount": add_words_amount,
                "add_userwords_amount": add_userwords_amount,
            }

            await send_user_data(data=data, server_url=METRIC_URL)

            return True

        except BaseException as e:
            logger.info(f"[UPLOAD USER WORDS] ERROR: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None
