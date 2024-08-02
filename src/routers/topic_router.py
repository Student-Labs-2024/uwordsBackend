from io import BytesIO
import logging
from typing import Annotated

from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, UploadFile, File

from src.database.models import User, Topic, SubTopic

from src.schemes.schemas import (
    SubTopicCreateDB,
    TopicCreate,
    SubTopicCreate,
    SubTopicIcon,
)

from src.services.services_config import mc
from src.services.topic_service import TopicService
from src.services.minio_uploader import MinioUploader

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.dependenes.chroma_service_fabric import (
    topic_service_fabric,
    subtopic_service_fabric,
)

from src.config import fastapi_docs_config as doc_data
from src.config.instance import MINIO_BUCKET_SUBTOPIC_ICONS, MINIO_HOST


topic_router_v1 = APIRouter(prefix="/api/v1/topic", tags=["Topic"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@topic_router_v1.post(
    "/add", name=doc_data.TOPIC_ADD_TITLE, description=doc_data.TOPIC_ADD_DESCRIPTION
)
async def add_topic(
    topic_data: TopicCreate,
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    if await topic_service.get([Topic.title == topic_data.title]):
        raise HTTPException(
            detail="Topic already exist", status_code=status.HTTP_400_BAD_REQUEST
        )

    return await topic_service.add(topic_data.model_dump())


@topic_router_v1.post(
    "/subtopic/add",
    name=doc_data.SUBTOPIC_ADD_TITLE,
    description=doc_data.SUBTOPIC_ADD_DESCRIPTION,
)
async def add_subtopic(
    subtopic_data: SubTopicCreate,
    topic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    topic = await topic_service.get([Topic.title == topic_title])

    if not topic:
        raise HTTPException(
            detail="Topic do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )

    if await subtopic_service.get(
        [SubTopic.title == subtopic_data.title, SubTopic.topic_title == topic_title]
    ):
        raise HTTPException(
            detail="Subtopic already exist", status_code=status.HTTP_400_BAD_REQUEST
        )

    subtopic = SubTopicCreateDB(title=subtopic_data.title, topic_title=topic.title)

    return await subtopic_service.add(subtopic.model_dump())


@topic_router_v1.post(
    "/subtopic/icon",
    name=doc_data.SUBTOPIC_ADD_ICON_TITLE,
    description=doc_data.SUBTOPIC_ADD_ICON_DESCRIPTION,
)
async def upload_subtopic_icon(
    subtopic_id: int,
    subtopic_icon: Annotated[UploadFile, File(description="A file read as UploadFile")],
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):

    subtopic = await subtopic_service.get([SubTopic.id == subtopic_id])

    if not subtopic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Subtopic not found"},
        )

    mimetype = await helper_utils.check_mime_type_icon(filename=subtopic_icon.filename)

    object_name = f"{subtopic.topic_title}_{subtopic.title}.svg"

    filedata = await subtopic_icon.read()

    bytes_file = BytesIO(filedata)
    bytes_file.seek(0)

    found_subtopic_icon_bucket = mc.bucket_exists(MINIO_BUCKET_SUBTOPIC_ICONS)
    if not found_subtopic_icon_bucket:
        await MinioUploader.create_bucket(MINIO_BUCKET_SUBTOPIC_ICONS)

    await MinioUploader.upload_object(
        bucket_name=MINIO_BUCKET_SUBTOPIC_ICONS,
        object_name=object_name,
        data=bytes_file,
        lenght=bytes_file.getbuffer().nbytes,
        type=mimetype,
    )

    picture_link = f"{MINIO_HOST}/{MINIO_BUCKET_SUBTOPIC_ICONS}/{object_name}"

    subtopic_data = SubTopicIcon(pictureLink=picture_link)

    return await subtopic_service.update_icon(
        subtopic_id=subtopic.id, subtopic_data=subtopic_data.model_dump()
    )


@topic_router_v1.get(
    "/get", name=doc_data.TOPIC_GET_TITLE, description=doc_data.TOPIC_GET_DESCRIPTION
)
async def get_topic(
    topic_title: str,
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    res = await topic_service.get([Topic.title == topic_title])
    if res:
        return res
    raise HTTPException(
        detail="Topic do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@topic_router_v1.get(
    "/subtopic/get",
    name=doc_data.SUBTOPIC_GET_TITLE,
    description=doc_data.SUBTOPIC_GET_DESCRIPTION,
)
async def get_subtopic(
    subtopic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    res = await subtopic_service.get([SubTopic.title == subtopic_title])
    if res:
        return res
    raise HTTPException(
        detail="Subtopic do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@topic_router_v1.get(
    "/all", name=doc_data.TOPIC_ALL_TITLE, description=doc_data.TOPIC_ALL_DESCRIPTION
)
async def get_all_topics(
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await topic_service.get_all()


@topic_router_v1.get(
    "/subtopic/all",
    name=doc_data.SUBTOPIC_ALL_TITLE,
    description=doc_data.SUBTOPIC_ALL_DESCRIPTION,
)
async def get_all_subtopics(
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await subtopic_service.get_all()


@topic_router_v1.get(
    "/subtopics",
    name=doc_data.SUBTOPIC_ALL_TOPIC_TITLE,
    description=doc_data.SUBTOPIC_ALL_TOPIC_DESCRIPTION,
)
async def get_all_subtopics(
    topic_title: str,
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    topic = await topic_service.get([Topic.title == topic_title])
    if topic:
        return topic.subtopics
    return []


@topic_router_v1.get(
    "/subtopic/check",
    response_model=str,
    name=doc_data.SUBTOPIC_CHECK_TITLE,
    description=doc_data.SUBTOPIC_CHECK_DESCRIPTION,
)
async def get_topic(
    word: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
) -> str:
    return await subtopic_service.check_word(word)


@topic_router_v1.delete(
    "/delete",
    name=doc_data.TOPIC_DELETE_TITLE,
    description=doc_data.TOPIC_DELETE_DESCRIPTION,
)
async def delete_topic(
    topic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    topic_service: Annotated[TopicService, Depends(topic_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    try:
        topic = await topic_service.get([Topic.title == topic_title])
        for subtopic in topic.subtopics:
            await subtopic_service.delete(
                [SubTopic.title == subtopic.title, str(subtopic.id)]
            )
        await topic_service.delete([Topic.title == topic_title])
        return topic_title
    except:
        raise HTTPException(
            detail="Topic do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )


@topic_router_v1.delete(
    "/subtopic/delete",
    name=doc_data.SUBTOPIC_DELETE_TITLE,
    description=doc_data.SUBTOPIC_DELETE_DESCRIPTION,
)
async def delete_subtopic(
    subtopic_title: str,
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    try:
        subtopic = await subtopic_service.get([SubTopic.title == subtopic_title])
        await subtopic_service.delete(
            [SubTopic.title == subtopic.title, str(subtopic.id)]
        )
    except:
        raise HTTPException(
            detail="Subtopic do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )
    return subtopic_title
