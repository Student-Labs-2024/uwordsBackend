from src.database.chroma_config import subtopic_collection
from src.database.models import (
    Achievement,
    Error,
    Feedback,
    User,
    UserWord,
    Word,
    Topic,
    SubTopic,
    Subscription,
    Bill,
    UserAchievement,
    UserWordStopList,
)

from src.utils.repository import SQLAlchemyRepository, ChromaRepository


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


class UserRepository(SQLAlchemyRepository):
    model = User


class SubscriptionRepository(SQLAlchemyRepository):
    model = Subscription


class FeedbackRepository(SQLAlchemyRepository):
    model = Feedback


class PaymentRepository(SQLAlchemyRepository):
    model = Bill


class AchievementRepository(SQLAlchemyRepository):
    model = Achievement


class UserAchievementRepository(SQLAlchemyRepository):
    model = UserAchievement


class UserWordStopListRepository(SQLAlchemyRepository):
    model = UserWordStopList
