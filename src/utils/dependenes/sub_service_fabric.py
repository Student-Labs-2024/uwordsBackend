from src.repositories.repositories import SubscriptionRepository
from src.services.subscription_service import SubscriptionService


def sub_service_fabric():
    return SubscriptionService(SubscriptionRepository())