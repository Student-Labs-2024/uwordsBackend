import os
import uuid
import logging
from typing import Annotated
from datetime import datetime
from pydub import AudioSegment

from fastapi import APIRouter, File, UploadFile, Depends

from src.celery.tasks import upload_audio_task, upload_youtube_task

from src.database.models import User, UserWord
from src.schemes.schemas import Audio, WordsIdsSchema, YoutubeLink

from src.config.instance import UPLOAD_DIR
from src.config import fastapi_docs_config as doc_data

from src.services.file_service import FileService
from src.services.error_service import ErrorService
from src.services.audio_service import AudioService
from src.services.user_word_service import UserWordService

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.dependenes.file_service_fabric import file_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric


user_router_v1 = APIRouter(prefix="/api/v1/user", tags=["User Words"])

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


@user_router_v1.get(
    "/words/get_words",
    name=doc_data.USER_WORDS_GET_TITLE,
    description=doc_data.USER_WORDS_GET_DESCRIPTION,
)
async def get_user_words(
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):

    user_words: list[UserWord] = await user_words_service.get_user_words(user.id)
    topics = []
    topics_titles = []
    titles: dict[str:list] = {}
    for user_word in user_words:
        if user_word.word.topic not in titles:
            titles[user_word.word.topic] = []
            topics_titles.append(user_word.word.topic)
            titles[user_word.word.topic].append(user_word.word.subtopic)
            topics.append(
                {
                    "topic_title": user_word.word.topic,
                    "subtopics": [
                        {
                            "subtopic_title": user_word.word.subtopic,
                            "words": [user_word],
                        }
                    ],
                }
            )
        else:
            index = topics_titles.index(user_word.word.topic)
            if user_word.word.subtopic in titles[user_word.word.topic]:
                sub_index = titles[user_word.word.topic].index(user_word.word.subtopic)
                topics[index]["subtopics"][sub_index]["words"].append(user_word)
            else:
                titles[user_word.word.topic].append(user_word.word.subtopic)
                topics[index]["subtopics"].append(
                    {"subtopic_title": user_word.word.subtopic, "words": [user_word]}
                )
    for topic in topics:
        not_in_subtopics = []
        subtopics_to_remove = []
        subtopics = topic["subtopics"]
        for subtopic in subtopics:
            if len(subtopic["words"]) < 8:
                not_in_subtopics.extend(subtopic["words"])
                subtopics_to_remove.append(subtopic["subtopic_title"])
        while True:
            if len(subtopics_to_remove) == 0:
                break
            index = titles[topic["topic_title"]].index(subtopics_to_remove[0])
            del titles[topic["topic_title"]][index]
            del subtopics[index]
            del subtopics_to_remove[0]
        subtopics.append(
            {"subtopic_title": "not_in_subtopics", "words": not_in_subtopics}
        )

    return topics


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
    words_for_study = await user_words_service.get_user_words_for_study(
        user_id=user.id, topic_title=topic_title, subtopic_title=subtopic_title
    )

    return words_for_study


@user_router_v1.post(
    "/words/study",
    name=doc_data.USER_WORDS_POST_STUDY_TITLE,
    description=doc_data.USER_WORDS_POST_STUDY_DESCRIPTION,
)
async def complete_user_words_learning(
    schema: WordsIdsSchema,
    user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    await user_words_service.update_progress_word(
        user_id=user.id, words_ids=schema.words_ids
    )
    return schema


@user_router_v1.post(
    "/audio",
    response_model=Audio,
    name=doc_data.UPLOAD_AUDIO_TITLE,
    description=doc_data.UPLOAD_AUDIO_DESCRIPTION,
)
async def upload_audio(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
    file_service: Annotated[FileService, Depends(file_service_fabric)],
    error_service: Annotated[ErrorService, Depends(error_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
) -> Audio:
    filename = file.filename
    await helper_utils.check_mime_type(filename)
    _, extension = os.path.splitext(filename)
    uploaded_at = datetime.now()

    filedata = await file.read()

    audio_name = f"audio_{uuid.uuid4()}{extension}"
    destination = UPLOAD_DIR / audio_name

    try:
        await file_service.add_file(destination, filedata)

        duration = int(len(AudioSegment.from_file(file=destination)) / 1000)

        logger.info(f"DURATION: {duration}")

    except Exception as e:
        logger.info(e)

    if extension != ".wav":
        title = f"{os.path.splitext(audio_name)[0]}_converted.wav"
        filepath = await AudioService.convert_audio(
            path=str(destination),
            title=title,
            error_service=error_service,
            user_id=user.id,
        )
        await file_service.delete_file(destination)

    else:
        filepath = destination

    response = Audio(
        filename=filename,
        extension=extension,
        filepath=filepath,
        uploaded_at=uploaded_at,
    )

    upload_audio_task.apply_async((filepath, user.id), countdown=1)

    return response


@user_router_v1.post(
    "/youtube",
    response_model=YoutubeLink,
    name=doc_data.UPLOAD_YOUTUBE_TITLE,
    description=doc_data.UPLOAD_YOUTUBE_DESCRIPTION,
)
async def upload_youtube_video(
    schema: YoutubeLink, user: User = Depends(auth_utils.get_active_current_user)
):
    await helper_utils.check_youtube_link(link=schema.link)
    upload_youtube_task.apply_async((schema.link, user.id), countdown=1)
    return schema
