from src.utils.repository import SQLAlchemyRepository, LocalFileRepository
from src.database.models import UserWord, Word


class UserWordRepository(SQLAlchemyRepository):
    model = UserWord


class WordRepository(SQLAlchemyRepository):
    model = Word
