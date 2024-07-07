import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from src.database import models
from src.schemes.schemas import Topic, SubTopic
from src.services.topic_service import TopicService
from src.utils.dependenes.chroma_service_fabric import topic_service_fabric, subtopic_service_fabric

topic_router_v1 = APIRouter(prefix="/api/v1/topic", tags=["Topic"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@topic_router_v1.post("/add", response_model=Topic)
async def add_topic(topic: Topic, topic_service: Annotated[TopicService, Depends(topic_service_fabric)], ):
    await topic_service.add(topic)
    return topic


@topic_router_v1.post("/subtopic/add", response_model=Topic)
async def add_subtopic(subtopic: SubTopic,
                       subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)], ):
    await subtopic_service.add(subtopic)
    return subtopic


@topic_router_v1.get("/get", response_model=Topic)
async def get_topic(topic_title: str, topic_service: Annotated[TopicService, Depends(topic_service_fabric)]):
    return await topic_service.get([models.Topic.title == topic_title])


@topic_router_v1.get("/subtopic/get", response_model=SubTopic)
async def get_subtopic(subtopic_title: str,
                       subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)]):
    return await subtopic_service.get([models.SubTopic.title == subtopic_title])


@topic_router_v1.get("/all")
async def get_all_topics(topic_service: Annotated[TopicService, Depends(topic_service_fabric)]):
    return await topic_service.get_all()


@topic_router_v1.get("/subtopic/all")
async def get_all_subtopics(subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)]):
    return await subtopic_service.get_all()


@topic_router_v1.get("/subtopics")
async def get_all_subtopics(topic_title: str, topic_service: Annotated[TopicService, Depends(topic_service_fabric)]):
    topic = await topic_service.get([models.Topic.title == topic_title])
    return topic.subtopics


@topic_router_v1.get("/subtopic/check", response_model=str)
async def get_topic(word: str, subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)]) -> str:
    return await subtopic_service.check_word(word)
