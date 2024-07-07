from src.database.chroma_config import topic_collection, subtopic_collection
from src.utils.repository import SQLAlchemyRepository, ChromaRepository
from src.database.models import UserWord, Word, Topic, SubTopic


class UserWordRepository(SQLAlchemyRepository):
    model = UserWord


class WordRepository(SQLAlchemyRepository):
    model = Word


class TopicRepository(SQLAlchemyRepository):
    model = Topic


class SubtopicRepository(ChromaRepository):
    collection = subtopic_collection
    model = SubTopic
