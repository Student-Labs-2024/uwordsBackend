import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from src.database import models
from src.schemes.schemas import Topic, SubTopic
from src.services.topic_service import TopicService
from src.utils.dependenes.chroma_service_fabric import topic_service_fabric, subtopic_service_fabric
from src.utils import auth as auth_utils

topic_router_v1 = APIRouter(prefix="/api/v1/topic", tags=["Topic"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@topic_router_v1.post("/add")
async def add_topic(
    topic: Topic, 
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)], 
    user: models.User = Depends(auth_utils.get_admin_user)
):
    res = await topic_service.add(topic)
    if not res:
        return topic
    return HTTPException(detail="Topic already exist", status_code=400)


@topic_router_v1.post("/subtopic/add")
async def add_subtopic(
    subtopic: SubTopic,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: models.User = Depends(auth_utils.get_admin_user)
):
    if await topic_service.get([models.Topic.title == subtopic.topic_title]):
        res = await subtopic_service.add(subtopic)
        if not res:
            return subtopic
        return HTTPException(detail="Subtopic already exist", status_code=400)
    else:
        return HTTPException(detail="Topic do not exist", status_code=400)


@topic_router_v1.get("/get")
async def get_topic(
    topic_title: str, 
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
):
    res = await topic_service.get([models.Topic.title == topic_title])
    if res:
        return res
    return HTTPException(detail="Topic do not exist", status_code=400)


@topic_router_v1.get("/subtopic/get")
async def get_subtopic(
    subtopic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
):
    res = await subtopic_service.get([models.SubTopic.title == subtopic_title])
    if res:
        return res
    return HTTPException(detail="Subtopic do not exist", status_code=400)


@topic_router_v1.get("/all")
async def get_all_topics(
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
):
    return await topic_service.get_all()


@topic_router_v1.get("/subtopic/all")
async def get_all_subtopics(
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
):
    return await subtopic_service.get_all()


@topic_router_v1.get("/subtopics")
async def get_all_subtopics(
    topic_title: str, 
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
):
    topic = await topic_service.get([models.Topic.title == topic_title])
    if topic:
        return topic.subtopics
    return []


@topic_router_v1.get("/subtopic/check", response_model=str)
async def get_topic(
    word: str, 
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: models.User = Depends(auth_utils.get_active_current_user)
) -> str:
    return await subtopic_service.check_word(word)


@topic_router_v1.delete('/delete')
async def delete_topic(
    topic_title: str, 
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: models.User = Depends(auth_utils.get_admin_user)
):
    try:
        topic = await topic_service.get([models.Topic.title == topic_title])
        for subtopic in topic.subtopics:
            await subtopic_service.delete([models.SubTopic.title == subtopic.title, str(subtopic.id)])
        await topic_service.delete([models.Topic.title == topic_title])
        return topic_title
    except:
        return HTTPException(detail="Topic do not exist", status_code=400)


@topic_router_v1.delete('/subtopic/delete')
async def delete_subtopic(
    subtopic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: models.User = Depends(auth_utils.get_admin_user)
):
    try:
        subtopic = await subtopic_service.get([models.SubTopic.title == subtopic_title])
        await subtopic_service.delete([models.SubTopic.title == subtopic.title, str(subtopic.id)])
    except:
        return HTTPException(detail="Subtopic do not exist", status_code=400)
    return subtopic_title
