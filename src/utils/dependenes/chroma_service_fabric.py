from src.services.topic_service import TopicService
from src.repositories.repositories import TopicRepository, SubtopicRepository


def topic_service_fabric():
    return TopicService(TopicRepository())


def subtopic_service_fabric():
    return TopicService(SubtopicRepository())
