from typing import List, Dict

from src.database.models import SubTopic, UserWord
from src.schemes.topic_schemas import SubtopicWords, TopicWords

from src.config.instance import DEFAULT_SUBTOPIC, DEFAULT_SUBTOPIC_ICON


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

        for topic, subtopics in topic_dict.items():
            topic_entry = TopicWords(title=topic, subtopics=[])
            unsorted_words = []

            for subtopic, words in subtopics.items():
                pictureLink = subtopics_icons[topic][subtopic]

                if len(words) < 8:
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

            result.append(topic_entry)

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
            if subtopic_word_count[user_word.word.subtopic] < 8:
                result.append(user_word)

        return result

    @staticmethod
    async def get_words(user_words: List[UserWord]) -> List:
        topics = []
        topics_titles = []
        titles: dict[str:list] = {}
        for user_word in user_words:
            if user_word.word.topic not in titles:
                titles[user_word.word.topic] = []
                topics_titles.append(user_word.word.topic)
                titles[user_word.word.topic].append(user_word.word.subtopic)
                topics.append(
                    {
                        "topic_title": user_word.word.topic,
                        "subtopics": [
                            {
                                "subtopic_title": user_word.word.subtopic,
                                "words": [user_word],
                            }
                        ],
                    }
                )
            else:
                index = topics_titles.index(user_word.word.topic)
                if user_word.word.subtopic in titles[user_word.word.topic]:
                    sub_index = titles[user_word.word.topic].index(
                        user_word.word.subtopic
                    )
                    topics[index]["subtopics"][sub_index]["words"].append(user_word)
                else:
                    titles[user_word.word.topic].append(user_word.word.subtopic)
                    topics[index]["subtopics"].append(
                        {
                            "subtopic_title": user_word.word.subtopic,
                            "words": [user_word],
                        }
                    )
        for topic in topics:
            not_in_subtopics = []
            subtopics_to_remove = []
            subtopics = topic["subtopics"]
            for subtopic in subtopics:
                if len(subtopic["words"]) < 8:
                    not_in_subtopics.extend(subtopic["words"])
                    subtopics_to_remove.append(subtopic["subtopic_title"])
            while True:
                if len(subtopics_to_remove) == 0:
                    break
                index = titles[topic["topic_title"]].index(subtopics_to_remove[0])
                del titles[topic["topic_title"]][index]
                del subtopics[index]
                del subtopics_to_remove[0]
            subtopics.append(
                {"subtopic_title": "not_in_subtopics", "words": not_in_subtopics}
            )

        return topics
