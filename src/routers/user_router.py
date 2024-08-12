import os
import uuid
import logging
from typing import Annotated, List

from fastapi import APIRouter, File, UploadFile, Depends, status, HTTPException

from src.celery.tasks import process_audio_task, process_youtube_task

from src.database.models import User, UserWord

from src.config.instance import (
    UPLOAD_DIR,
    DEFAULT_SUBTOPIC,
    FASTAPI_SECRET,
)
from src.config import fastapi_docs_config as doc_data
from src.schemes.admin_schemas import BotWords
from src.schemes.audio_schemas import YoutubeLink
from src.schemes.topic_schemas import TopicWords
from src.schemes.util_schemas import CustomResponse
from src.schemes.word_schemas import WordsIdsSchema
from src.services.achievement_service import AchievementService
from src.services.response_service import ResponseService
from src.services.text_service import TextService
from src.services.user_achievement_service import UserAchievementService
from src.services.word_service import WordService

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils.dependenes.file_service_fabric import file_service_fabric
from src.utils.dependenes.user_achievement_fabric import user_achievement_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric

from src.services.file_service import FileService
from src.services.user_service import UserService
from src.services.error_service import ErrorService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService
from src.utils.dependenes.word_service_fabric import word_service_fabric

user_router_v1 = APIRouter(prefix="/api/v1/user", tags=["User Words"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@user_router_v1.get(
    "/topics",
    name=doc_data.USER_TOPICS_GET_TITLE,
    description=doc_data.USER_TOPICS_GET_DESCRIPTION,
    response_model=List[TopicWords],
)
async def get_user_topics(
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    user_words = await user_words_service.get_user_words(user_id=user.id)
    subtopics = await subtopic_service.get_all()

    return await ResponseService.get_user_topic(
        subtopics=subtopics, user_words=user_words
    )


@user_router_v1.get(
    "/subtopic/words",
    name=doc_data.USER_TOPICS_GET_SUBTOPIC_WORDS_TITLE,
    description=doc_data.USER_TOPICS_GET_SUBTOPIC_WORDS_DESCRIPTION,
)
async def get_user_words_by_subtopic(
    topic_title: str,
    subtopic_title: str,
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if subtopic_title != DEFAULT_SUBTOPIC:
        return await user_words_service.get_user_words_by_filter(
            user_id=user.id, topic_title=topic_title, subtopic_title=subtopic_title
        )

    user_words = await user_words_service.get_user_words_by_filter(
        user_id=user.id, topic_title=topic_title
    )

    return await ResponseService.get_user_words_by_subtopic(user_words=user_words)


@user_router_v1.get(
    "/words/study",
    name=doc_data.USER_WORDS_GET_STUDY_TITLE,
    description=doc_data.USER_WORDS_GET_STUDY_DESCRIPTION,
)
async def get_user_words_for_study(
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
    topic_title: str | None = None,
    subtopic_title: str | None = None,
):
    if not user.subscription_type and user.energy < 10:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Energy limit ran out"
        )

    words_for_study = await user_words_service.get_user_words_for_study(
        user_id=user.id, topic_title=topic_title, subtopic_title=subtopic_title
    )

    return words_for_study


@user_router_v1.post(
    "/words/study",
    response_model=CustomResponse,
    name=doc_data.USER_WORDS_POST_STUDY_TITLE,
    description=doc_data.USER_WORDS_POST_STUDY_DESCRIPTION,
)
async def complete_user_words_learning(
    schema: WordsIdsSchema,
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    achievements_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user_achievements_service: Annotated[
        UserAchievementService, Depends(user_achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if not user.subscription_type and user.energy < 10:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Energy limit ran out"
        )

    await user_words_service.update_progress_word(
        user_id=user.id, words_ids=schema.words_ids
    )

    user_achievements = await achievements_service.get_user_achievements(
        user_id=user.id
    )

    await user_service.update_learning_days(uid=user.id)

    await user_service.update_user(
        user_id=user.id, user_data={"energy": user.energy - 10}
    )

    await user_service.check_user_achievemets(
        user_id=user.id,
        user_achievements=user_achievements,
        user_achievement_service=user_achievements_service,
    )

    return CustomResponse(status_code=status.HTTP_200_OK, message="Progress updated!")


@user_router_v1.post(
    "/audio",
    response_model=CustomResponse,
    name=doc_data.UPLOAD_AUDIO_TITLE,
    description=doc_data.UPLOAD_AUDIO_DESCRIPTION,
)
async def upload_audio(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
    file_service: Annotated[FileService, Depends(file_service_fabric)],
    error_service: Annotated[ErrorService, Depends(error_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if not user.subscription_type and user.allowed_audio_seconds == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seconds limit ran out"
        )

    filename = file.filename

    await helper_utils.check_mime_type(filename)

    _, extension = os.path.splitext(filename)

    filedata = await file.read()

    title = f"audio_{uuid.uuid4()}"

    audio_name = f"{title}{extension}"
    destination = UPLOAD_DIR / audio_name

    try:
        await file_service.add_file(destination, filedata)

    except Exception as e:
        logger.info(e)

    process_audio_task.apply_async(
        kwargs={"path": destination.__str__(), "title": title, "user_id": user.id},
        countdown=1,
    )

    response = CustomResponse(
        status_code=status.HTTP_200_OK, message="Processing started"
    )

    return response


@user_router_v1.post(
    "/youtube",
    response_model=CustomResponse,
    name=doc_data.UPLOAD_YOUTUBE_TITLE,
    description=doc_data.UPLOAD_YOUTUBE_DESCRIPTION,
)
async def upload_youtube_video(
    schema: YoutubeLink, user: User = Depends(auth_utils.get_active_current_user)
):
    if not user.subscription_type and user.allowed_video_seconds == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seconds limit ran out"
        )

    await helper_utils.check_youtube_link(link=schema.link)

    process_youtube_task.apply_async(
        kwargs={
            "link": schema.link,
            "user_id": user.id,
        },
        countdown=1,
    )

    return CustomResponse(status_code=status.HTTP_200_OK, message="Processing started")


@user_router_v1.post(
    "/bot_word",
    response_model=BotWords,
    name=doc_data.UPLOAD_YOUTUBE_TITLE,
    description=doc_data.UPLOAD_YOUTUBE_DESCRIPTION,
)
async def words_from_bot(
    data: BotWords,
    user_word_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    error_service: Annotated[ErrorService, Depends(error_service_fabric)],
    word_service: Annotated[WordService, Depends(word_service_fabric)],
    subtopic_service: Annotated[TopicService, Depends(subtopic_service_fabric)],
    user_service: Annotated[UserService, Depends(user_service_fabric)],
):
    user: User = await user_service.get_user_by_id(data.user_id)
    if not user.subscription_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "You are not subscribed"},
        )
    if data.secret == FASTAPI_SECRET:
        translated_words = await TextService.get_translated_clear_text(
            data.text, error_service, data.user_id
        )

        await user_word_service.upload_user_words(
            user_words=translated_words,
            user_id=data.user_id,
            word_service=word_service,
            subtopic_service=subtopic_service,
            error_service=error_service,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"msg": "Wrong secret"},
    )
