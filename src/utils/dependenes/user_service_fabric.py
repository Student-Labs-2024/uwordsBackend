from src.services.user_service import UserService
from src.repositories.repositories import UserRepository


def user_service_fabric():
    return UserService(UserRepository())
