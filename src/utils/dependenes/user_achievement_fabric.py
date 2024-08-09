from src.services.user_achievement_service import UserAchievementService
from src.repositories.repositories import UserAchievementRepository


def user_achievement_service_fabric():
    return UserAchievementService(UserAchievementRepository())
