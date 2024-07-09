from src.database.chroma_config import subtopic_collection
from src.utils.repository import SQLAlchemyRepository, ChromaRepository
from src.database.models import Error, UserWord, Word, Topic, SubTopic


class UserWordRepository(SQLAlchemyRepository):
    model = UserWord


class WordRepository(SQLAlchemyRepository):
    model = Word


class TopicRepository(SQLAlchemyRepository):
    model = Topic


class SubtopicRepository(ChromaRepository):
    collection = subtopic_collection
    model = SubTopic

class ErrorRepository(SQLAlchemyRepository):
    model = Error
