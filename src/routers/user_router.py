import os
import uuid
import logging
from typing import Annotated, List

from fastapi import APIRouter, File, UploadFile, Depends, status, HTTPException

from src.celery.tasks import process_audio_task, process_youtube_task, process_text_task

from src.database.models import User

from src.config.instance import (
    UPLOAD_DIR,
    DEFAULT_SUBTOPIC,
    SERVICE_SECRET,
)
from src.config import fastapi_docs_config as doc_data
from src.schemes.admin_schemas import BotPromo, BotWords
from src.schemes.audio_schemas import YoutubeLink
from src.schemes.topic_schemas import TopicWords
from src.schemes.user_schemas import UserWordDumpSchema
from src.schemes.user_word_stop_list_schemas import UserWordStopListCreate
from src.schemes.util_schemas import CustomResponse
from src.schemes.word_schemas import WordsIdsSchema
from src.services.achievement_service import AchievementService
from src.services.subscription_service import SubscriptionService
from src.services.user_achievement_service import UserAchievementService
from src.services.user_word_stop_list_service import UserWordStopListService

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils.dependenes.file_service_fabric import file_service_fabric
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_achievement_fabric import user_achievement_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric
from src.utils.dependenes.user_word_stop_list_service_fabric import (
    user_word_stop_list_service_fabric,
)

from src.services.file_service import FileService
from src.services.user_service import UserService
from src.services.error_service import ErrorService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService
from src.utils.exceptions import UserNotFoundException, UserNotSubscribedException
from src.utils.logger import words_router_logger

user_router_v1 = APIRouter(prefix="/api/v1/user", tags=["User Words"])


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

    return await user_words_service.get_user_topic(
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

    return await user_words_service.get_unsorted_user_words(user_words=user_words)


@user_router_v1.get(
    "/debug/all_words",
    response_model=List[UserWordDumpSchema],
    name=doc_data.USER_TOPICS_GET_SUBTOPIC_WORDS_TITLE,
    description=doc_data.USER_TOPICS_GET_SUBTOPIC_WORDS_DESCRIPTION,
)
async def debug_get_all_userwords(
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await user_words_service.get_user_words(user_id=user.id)


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

    return await user_words_service.get_user_words_for_study(
        user_id=user.id, topic_title=topic_title, subtopic_title=subtopic_title
    )


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
        user_id=user.id, uwords_uid=user.uwords_uid, words_ids=schema.words_ids
    )

    await user_service.update_user(
        user_id=user.id, user_data={"energy": user.energy - 10}
    )

    await user_service.update_learning_days(uid=user.id)

    await user_service.check_user_achievemets(
        user_id=user.id,
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
        words_router_logger.error(e)

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
    response_model=CustomResponse,
    name=doc_data.UPLOAD_BOT_WORDS_TITLE,
    description=doc_data.UPLOAD_BOT_WORDS_DESCRIPTION,
)
async def words_from_bot(
    data: BotWords,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    token=Depends(auth_utils.check_secret_token),
):
    user: User = await user_service.get_user_by_uwords_uid(uwords_uid=data.uwords_uid)
    if not user.subscription_type:
        raise UserNotSubscribedException()

    process_text_task.apply_async(
        kwargs={
            "text": data.text,
            "user_id": user.id,
        },
        countdown=1,
    )

    return CustomResponse(status_code=status.HTTP_200_OK, message="Processing started")


@user_router_v1.post(
    "/bot_audio",
    response_model=CustomResponse,
    name=doc_data.UPLOAD_BOT_AUDIO_TITLE,
    description=doc_data.UPLOAD_BOT_AUDIO_DESCRIPTION,
)
async def audio_from_bot(
    uwords_uid: str,
    audio_file: Annotated[UploadFile, File(description="A file read as UploadFile")],
    file_service: Annotated[FileService, Depends(file_service_fabric)],
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    token=Depends(auth_utils.check_secret_token),
):
    user: User = await user_service.get_user_by_uwords_uid(uwords_uid=uwords_uid)

    if not user:
        raise UserNotFoundException()

    if not user.subscription_type:
        raise UserNotSubscribedException()

    filename = audio_file.filename

    await helper_utils.check_mime_type(filename)

    _, extension = os.path.splitext(filename)

    filedata = await audio_file.read()

    title = f"audio_{uuid.uuid4()}"

    audio_name = f"{title}{extension}"
    destination = UPLOAD_DIR / audio_name

    try:
        await file_service.add_file(destination, filedata)

    except Exception as e:
        words_router_logger.error(e)

    process_audio_task.apply_async(
        kwargs={"path": destination.__str__(), "title": title, "user_id": user.id},
        countdown=1,
    )

    response = CustomResponse(
        status_code=status.HTTP_200_OK, message="Processing started"
    )

    return response


@user_router_v1.post(
    "/promo",
    response_model=CustomResponse,
    name=doc_data.BOT_PROMO_TITLE,
    description=doc_data.BOT_PROMO_DESCRIPTION,
)
async def audio_from_bot(
    promo_data: BotPromo,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    token=Depends(auth_utils.check_secret_token),
):
    user: User = await user_service.get_user_by_uwords_uid(
        uwords_uid=promo_data.uwords_uid
    )

    if not user:
        raise UserNotFoundException()

    sub = await sub_service.get_sub_by_promo(promo=promo_data.promo)

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Promocode not found"},
        )

    await user_service.update_user(
        user_id=user.id, user_data={"promo": promo_data.promo}
    )

    return CustomResponse(
        status_code=200,
        message=f"Promo code successfully applied! New price {sub.promo_price_str}. Check your personal account",
    )


@user_router_v1.delete(
    "/word",
    response_model=CustomResponse,
    name=doc_data.DELETE_USER_WORD_TITLE,
    description=doc_data.DELETE_USER_WORD_DESCRIPTION,
)
async def delete_word(
    user_word_id: int,
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user_word_stop_list_service: Annotated[
        UserWordStopListService, Depends(user_word_stop_list_service_fabric)
    ],
    user: User = Depends(auth_utils.get_active_current_user),
):

    user_word = await user_words_service.get_user_word(
        user_id=user.id, user_word_id=user_word_id
    )

    if not user_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "User word not found"}
        )

    user_word_stop_data = UserWordStopListCreate(
        user_id=user_word.user_id, word_id=user_word.word_id
    )

    await user_word_stop_list_service.add_one(
        user_word_stop_data=user_word_stop_data.model_dump()
    )

    await user_words_service.delete_one(userword_id=user_word.id)

    return CustomResponse(status_code=status.HTTP_200_OK, message="User word deleted!")
