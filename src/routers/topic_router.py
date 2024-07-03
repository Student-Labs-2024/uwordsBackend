import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemes.schemas import Topic
from src.services.topic_service import TopicService
from src.utils.dependenes.chroma_service_fabric import topic_service_fabric, subtopic_service_fabric

topic_router_v1 = APIRouter(prefix="/api/v1/topic", tags=["Topic"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@topic_router_v1.post("/add", response_model=Topic)
async def add_topic(topic: Topic, topic_service: Annotated[TopicService, Depends(topic_service_fabric)], ):
    await topic_service.add_topic(topic)
    return topic


@topic_router_v1.post("/subtopic/add", response_model=Topic)
async def add_subtopic(subtopic: Topic, subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)], ):
    await subtopic_service.add_topic(subtopic)
    return subtopic


@topic_router_v1.get("/get", response_model=Topic)
async def get_topic(topic_id: str, topic_service: Annotated[TopicService, Depends(topic_service_fabric)]) -> Topic:
    return await topic_service.get_topic(topic_id)


@topic_router_v1.get("/subtopic/get", response_model=Topic)
async def get_subtopic(subtopic_id: str,
                       subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)]) -> Topic:
    return await subtopic_service.get_topic(subtopic_id)


@topic_router_v1.get("/check", response_model=str)
async def get_topic(word: str, topic_service: Annotated[TopicService, Depends(topic_service_fabric)]) -> str:
    return await topic_service.check_word(word)


@topic_router_v1.get("/subtopic/check", response_model=str)
async def get_topic(word: str, subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)]) -> str:
    return await subtopic_service.check_word(word)
