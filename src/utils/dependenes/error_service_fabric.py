from src.services.error_service import ErrorService
from src.repositories.repositories import ErrorRepository


def error_service_fabric():
    return ErrorService(ErrorRepository())
