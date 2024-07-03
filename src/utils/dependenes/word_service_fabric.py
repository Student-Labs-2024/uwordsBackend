from src.repositories.repositories import WordRepository
from src.services.word_service import WordService


def word_service_fabric():
    return WordService(WordRepository())
