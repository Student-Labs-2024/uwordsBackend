from src.repositories.repositories import TopicRepository, SubtopicRepository
from src.services.topic_service import TopicService


def topic_service_fabric():
    return TopicService(TopicRepository())


def subtopic_service_fabric():
    return TopicService(SubtopicRepository())
