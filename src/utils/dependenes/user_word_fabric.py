from src.repositories.repositories import UserWordRepository
from src.services.user_word_service import UserWordService


def user_word_service_fabric():
    return UserWordService(UserWordRepository())
