from src.services.user_word_stop_list_service import UserWordStopListService
from src.repositories.repositories import UserWordStopListRepository


def user_word_stop_list_service_fabric():
    return UserWordStopListService(UserWordStopListRepository())
