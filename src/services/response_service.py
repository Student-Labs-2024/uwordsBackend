import logging
from typing import List, Dict

from src.database.models import SubTopic, UserWord
from src.schemes.topic_schemas import SubtopicWords, TopicWords

from src.config.instance import (
    DEFAULT_SUBTOPIC,
    DEFAULT_SUBTOPIC_ICON,
    SUBTOPIC_COUNT_WORDS,
)


class ResponseService:
    @staticmethod
    async def get_user_topic(
        subtopics: List[SubTopic], user_words: List[UserWord]
    ) -> List:
        subtopics_icons: Dict[str, Dict[str, str]] = {}

        for subtopic in subtopics:
            if subtopic.topic_title not in subtopics_icons:
                subtopics_icons[subtopic.topic_title] = {}
            subtopics_icons[subtopic.topic_title][subtopic.title] = subtopic.pictureLink

        topic_dict: Dict[str, Dict[str, List[UserWord]]] = {}

        for user_word in user_words:
            topic = user_word.word.topic
            subtopic = user_word.word.subtopic

            if topic not in topic_dict:
                topic_dict[topic] = {}
            if subtopic not in topic_dict[topic]:
                topic_dict[topic][subtopic] = []

            topic_dict[topic][subtopic].append(user_word)

        result = []
        in_progress_subtopics = []

        for topic, subtopics in topic_dict.items():
            topic_entry = TopicWords(title=topic, subtopics=[])
            unsorted_words = []

            for subtopic, words in subtopics.items():
                pictureLink = subtopics_icons[topic][subtopic]

                if len(words) < SUBTOPIC_COUNT_WORDS:
                    unsorted_words.extend(words)
                else:
                    word_count = len(words)
                    progress = round(
                        sum(word.progress for word in words) / (word_count * 4) * 100
                    )
                    subtopic_word = SubtopicWords(
                        title=subtopic,
                        word_count=word_count,
                        progress=progress,
                        pictureLink=pictureLink,
                    )

                    topic_entry.subtopics.append(subtopic_word)

                    if progress > 0:
                        in_progress_subtopics.append(subtopic_word)

            if unsorted_words:
                word_count = len(unsorted_words)
                progress = round(
                    sum(word.progress for word in unsorted_words)
                    / (word_count * 4)
                    * 100
                )
                subtopic_word = SubtopicWords(
                    title=DEFAULT_SUBTOPIC,
                    word_count=word_count,
                    progress=progress,
                    pictureLink=DEFAULT_SUBTOPIC_ICON,
                )
                topic_entry.subtopics.append(subtopic_word)

                if progress > 0:
                    in_progress_subtopics.append(subtopic_word)

            result.append(topic_entry)

        if in_progress_subtopics:
            in_progress_topic = TopicWords(
                title="In Progress", subtopics=in_progress_subtopics
            )
            result.insert(0, in_progress_topic)

        return result

    @staticmethod
    async def get_user_words_by_subtopic(user_words: List[UserWord]) -> List:
        result = []
        subtopic_word_count = {}

        for user_word in user_words:
            subtopic = user_word.word.subtopic
            if subtopic not in subtopic_word_count:
                subtopic_word_count[subtopic] = 0
            subtopic_word_count[subtopic] += 1

        for user_word in user_words:
            if subtopic_word_count[user_word.word.subtopic] < SUBTOPIC_COUNT_WORDS:
                result.append(user_word)

        return result
