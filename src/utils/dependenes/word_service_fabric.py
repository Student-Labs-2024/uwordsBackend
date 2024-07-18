from src.services.word_service import WordService
from src.repositories.repositories import WordRepository


def word_service_fabric():
    return WordService(WordRepository())
