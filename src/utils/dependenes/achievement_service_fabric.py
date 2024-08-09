from src.services.achievement_service import AchievementService
from src.repositories.repositories import AchievementRepository


def achievement_service_fabric():
    return AchievementService(AchievementRepository())
