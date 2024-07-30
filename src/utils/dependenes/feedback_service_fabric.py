from src.services.feedback_service import FeedbackService
from src.repositories.repositories import FeedbackRepository


def feedback_service_fabric():
    return FeedbackService(FeedbackRepository())
