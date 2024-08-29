import logging
from datetime import datetime, timedelta
import random
from typing import Optional, Union, List, Dict
from dateutil.relativedelta import relativedelta

from src.schemes.error_schemas import ErrorCreate
from src.schemes.topic_schemas import SubtopicWords, TopicWords

from src.services.user_word_stop_list_service import UserWordStopListService
from src.utils.metric import send_user_data
from src.utils.repository import AbstractRepository

from src.database.models import UserWord, Word, SubTopic

from src.services.services_config import mc
from src.services.user_service import UserService
from src.services.word_service import WordService
from src.services.error_service import ErrorService
from src.services.topic_service import TopicService
from src.services.minio_uploader import MinioUploader
from src.services.censore_service import CensoreFilter
from src.services.user_achievement_service import UserAchievementService

from src.config.instance import (
    DEFAULT_SUBTOPIC_ICON,
    METRIC_URL,
    STUDY_DELAY,
    DEFAULT_SUBTOPIC,
    STUDY_MAX_PROGRESS,
    STUDY_WORDS_AMOUNT,
    SUBTOPIC_COUNT_WORDS,
    STUDY_RANDOM_PIC,
)
from src.utils.logger import user_service_logger


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
            user_service_logger.error(f"[GET USER WORDS By FILTER] ERROR: {e}")
            return []

    async def get_user_word(
        self, user_id: int, user_word_id: int
    ) -> Union[UserWord, None]:
        try:
            user_word: UserWord = await self.repo.get_one(
                [UserWord.user_id == user_id, UserWord.id == user_word_id]
            )
            return user_word

        except BaseException as e:
            user_service_logger.error(f"[GET USER WORD] ERROR: {e}")
            return None

    async def get_user_word_by_word_id(
        self, user_id: int, word_id: int
    ) -> Union[UserWord, None]:
        try:
            user_word: UserWord = await self.repo.get_one(
                [UserWord.user_id == user_id, UserWord.word_id == word_id]
            )
            return user_word

        except BaseException as e:
            user_service_logger.error(f"[GET USER WORD by WORD ID] ERROR: {e}")
            return None

    async def create_subtopic_icons(
        self, subtopics: List[SubTopic]
    ) -> Dict[str, Dict[str, str]]:
        subtopics_icons: Dict[str, Dict[str, str]] = {}

        for subtopic in subtopics:
            if subtopic.topic_title not in subtopics_icons:
                subtopics_icons[subtopic.topic_title] = {}
            subtopics_icons[subtopic.topic_title][subtopic.title] = subtopic.pictureLink

        return subtopics_icons

    async def create_topic_dict(
        self, user_words: List[UserWord]
    ) -> Dict[str, Dict[str, List[UserWord]]]:
        topic_dict: Dict[str, Dict[str, List[UserWord]]] = {}

        for user_word in user_words:
            topic = user_word.word.topic
            subtopic = user_word.word.subtopic
            topic_dict.setdefault(topic, {}).setdefault(subtopic, []).append(user_word)

        return topic_dict

    async def count_progress(self, words: List[UserWord], word_count: int) -> float:
        return round(
            sum(word.progress for word in words)
            / (word_count * STUDY_MAX_PROGRESS)
            * 100
        )

    async def create_subtopic(
        self,
        topic: str,
        word_count: int,
        words: List[UserWord],
        subtopics_icons: Dict[str, Dict[str, str]],
        subtopic: Optional[str] = None,
    ) -> SubtopicWords:
        progress = await self.count_progress(words=words, word_count=word_count)
        pictureLink = subtopics_icons.get(topic).get(subtopic, DEFAULT_SUBTOPIC_ICON)

        return SubtopicWords(
            title=subtopic or DEFAULT_SUBTOPIC,
            topic_title=topic,
            word_count=word_count,
            progress=progress,
            pictureLink=pictureLink,
        )

    async def get_user_topic(
        self, subtopics: List[SubTopic], user_words: List[UserWord]
    ) -> List:

        subtopics_icons = await self.create_subtopic_icons(subtopics=subtopics)
        topic_dict = await self.create_topic_dict(user_words=user_words)

        result = []
        in_progress_subtopics = []

        for topic, subtopics in topic_dict.items():
            topic_result = TopicWords(title=topic, subtopics=[])
            unsorted_words: List[UserWord] = []

            for subtopic, words in subtopics.items():
                word_count = len(words)
                if word_count < SUBTOPIC_COUNT_WORDS:
                    unsorted_words.extend(words)
                else:
                    subtopic_result = await self.create_subtopic(
                        topic=topic,
                        word_count=word_count,
                        words=words,
                        subtopics_icons=subtopics_icons,
                        subtopic=subtopic,
                    )

                    topic_result.subtopics.append(subtopic_result)

                    if subtopic_result.progress > 0:
                        in_progress_subtopics.append(subtopic_result)

            if unsorted_words:
                word_count = len(unsorted_words)
                subtopic_result = await self.create_subtopic(
                    topic=topic,
                    word_count=word_count,
                    words=unsorted_words,
                    subtopics_icons=subtopics_icons,
                )
                topic_result.subtopics.append(subtopic_result)
                if subtopic_result.progress > 0:
                    in_progress_subtopics.append(subtopic_result)

            result.append(topic_result)

        if in_progress_subtopics:
            result.insert(
                0, TopicWords(title="In Progress", subtopics=in_progress_subtopics)
            )

        return result

    async def get_unsorted_user_words(
        self, user_words: List[UserWord]
    ) -> List[UserWord]:
        unsorted_words = []
        subtopic_word_count = {}

        for user_word in user_words:
            subtopic = user_word.word.subtopic
            if subtopic not in subtopic_word_count:
                subtopic_word_count[subtopic] = 0
            subtopic_word_count[subtopic] += 1

        for user_word in user_words:
            if subtopic_word_count[user_word.word.subtopic] < SUBTOPIC_COUNT_WORDS:
                unsorted_words.append(user_word)

        return unsorted_words

    async def get_user_words_for_study(
        self,
        user_id: int,
        topic_title: Union[str, None] = None,
        subtopic_title: Union[str, None] = None,
    ) -> Union[List[UserWord], List]:
        try:
            filters = [UserWord.user_id == user_id]

            if topic_title:
                filters.append(UserWord.word.has(Word.topic == topic_title))

            if subtopic_title and subtopic_title != DEFAULT_SUBTOPIC:
                filters.append(UserWord.word.has(Word.subtopic == subtopic_title))

            user_words: List[UserWord] = await self.repo.get_all_by_filter(
                filters=filters, order=UserWord.progress.desc()
            )
            words_pictures = [word.word.pictureLink for word in user_words]
            if len(user_words) < STUDY_RANDOM_PIC:
                additional_words: List[UserWord] = await self.repo.get_all_by_filter(
                    filters=[UserWord.user_id == user_id]
                )
                additional_words_pictures = [
                    word.word.pictureLink for word in additional_words
                ]
                while len(words_pictures) < STUDY_RANDOM_PIC and len(
                    words_pictures
                ) < len(additional_words):
                    for additional_words_picture in additional_words_pictures:
                        if additional_words_picture not in words_pictures:
                            words_pictures.append(additional_words_picture)
            if subtopic_title == DEFAULT_SUBTOPIC:
                user_words = await self.get_unsorted_user_words(user_words=user_words)

            words_for_study = await self.filter_words_for_study(user_words=user_words)
            words_for_study = [word.__dict__ for word in words_for_study]
            for word in words_for_study:
                word["additional_pictures"] = random.sample(words_pictures, 3)
            return words_for_study

        except BaseException as e:
            user_service_logger.error(f"[GET USER WORDS FOR STUDY] ERROR: {e}")
            return []

    async def filter_words_for_study(
        self, user_words: List[UserWord]
    ) -> List[UserWord]:
        time_now = datetime.now()
        words_for_study = []

        for user_word in user_words:
            if len(words_for_study) >= STUDY_WORDS_AMOUNT:
                break

            if user_word.progress >= STUDY_MAX_PROGRESS:
                continue

            if not user_word.latest_study:
                words_for_study.append(user_word)
                continue

            delta: timedelta = time_now - user_word.latest_study

            if delta.total_seconds() >= STUDY_DELAY:
                words_for_study.append(user_word)

        return words_for_study

    async def update_progress_word(
        self, user_id: int, uwords_uid: str, words_ids: List[int]
    ) -> None:
        try:
            time_now = datetime.now()
            learned = 0

            for word_id in words_ids:
                user_word: UserWord = await self.repo.get_one(
                    [UserWord.user_id == user_id, UserWord.id == word_id]
                )
                if user_word.progress >= STUDY_MAX_PROGRESS:
                    continue

                upd_user_word: UserWord = await self.repo.update_one(
                    [UserWord.user_id == user_id, UserWord.id == word_id],
                    {"latest_study": time_now, "progress": user_word.progress + 1},
                )
                if upd_user_word.progress == STUDY_MAX_PROGRESS:
                    learned += 1

            data = {"uwords_uid": uwords_uid, "learned_amount": learned}

            await send_user_data(data=data, server_url=METRIC_URL)

        except BaseException as e:
            user_service_logger.error(f"[UPLOAD USER WORD] ERROR: {e}")

    async def upload_user_word(
        self,
        new_word: Dict,
        user_id: int,
        word_service: WordService,
        subtopic_service: TopicService,
        error_service: ErrorService,
        user_word_stop_list_service: UserWordStopListService,
    ) -> bool:
        try:
            time_now = datetime.now()

            en_value = new_word.get("enValue", None)
            ru_value = new_word.get("ruValue", None)
            frequency = new_word.get("frequency", 0)

            if CensoreFilter.is_censore(text=ru_value):
                user_service_logger.info(f"[UPLOAD WORD] CENSORE: {ru_value}")
                return None

            if CensoreFilter.is_censore(text=en_value):
                user_service_logger.info(f"[UPLOAD WORD] CENSORE: {en_value}")
                return None

            word = await word_service.get_word(en_value=en_value)

            if word:
                stop_word_list = await user_word_stop_list_service.get_user_word_stop(
                    user_id=user_id, word_id=word.id
                )

                if stop_word_list:
                    if time_now < stop_word_list.delete_at + relativedelta(months=1):
                        return False

                    else:
                        await user_word_stop_list_service.delete_one(
                            user_word_stop_id=stop_word_list.id
                        )

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

            user_word = await self.get_user_word_by_word_id(
                user_id=user_id, word_id=word.id
            )
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

            return True

        except BaseException as e:
            user_service_logger.error(f"[UPLOAD USER WORD] ERROR: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return False

    async def upload_user_words(
        self,
        user_words: List[Dict],
        user_id: int,
        uwords_uid: str,
        word_service: WordService,
        subtopic_service: TopicService,
        error_service: ErrorService,
        user_achievement_service: UserAchievementService,
        user_service: UserService,
        user_word_stop_list_service: UserWordStopListService,
    ) -> bool:
        try:
            await MinioUploader.check_buckets()

            add_words_amount = 0
            add_userwords_amount = len(user_words)

            for user_word in user_words:
                is_new = await self.upload_user_word(
                    new_word=user_word,
                    user_id=user_id,
                    word_service=word_service,
                    subtopic_service=subtopic_service,
                    error_service=error_service,
                    user_word_stop_list_service=user_word_stop_list_service,
                )
                if is_new:
                    add_words_amount += 1

            data = {
                "uwords_uid": uwords_uid,
                "add_words_amount": add_words_amount,
                "add_userwords_amount": add_userwords_amount,
            }

            await send_user_data(data=data, server_url=METRIC_URL)

            user_achievements = await user_achievement_service.get_user_achievements(
                user_id=user_id
            )

            await user_service.check_user_achievemets(
                user_id=user_id,
                user_achievements=user_achievements,
                user_achievement_service=user_achievement_service,
            )

            return True

        except BaseException as e:
            user_service_logger.error(f"[UPLOAD USER WORDS] ERROR: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    async def delete_one(self, userword_id: int) -> None:
        await self.repo.delete_one(filters=[UserWord.id == userword_id])
