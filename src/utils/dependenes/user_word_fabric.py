from src.services.user_word_service import UserWordService
from src.repositories.repositories import UserWordRepository


def user_word_service_fabric():
    return UserWordService(UserWordRepository())
