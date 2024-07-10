from src.repositories.repositories import ErrorRepository
from src.services.error_service import ErrorService


def error_service_fabric():
    return ErrorService(ErrorRepository())