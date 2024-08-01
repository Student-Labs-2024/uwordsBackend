import json
import os
import uuid
import logging
from typing import Annotated, List, Dict
from datetime import datetime
from pydub import AudioSegment

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status

from src.celery.tasks import process_audio_task, process_youtube_task

from src.database.models import User, UserWord
from src.schemes.schemas import (
    Audio,
    WordsIdsSchema,
    YoutubeLink,
    TopicWords,
    SubtopicWords,
    UserWordDumpSchema,
)

from src.config.instance import UPLOAD_DIR, DEFAULT_SUBTOPIC, DEFAULT_SUBTOPIC_ICON
from src.config import fastapi_docs_config as doc_data

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.dependenes.file_service_fabric import file_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric

from src.services.file_service import FileService
from src.services.user_service import UserService
from src.services.error_service import ErrorService
from src.services.audio_service import AudioService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService

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

    subtopics_icons: Dict[str, Dict[str, str]] = {}

    for subtopic in subtopics:
        if subtopic.topic_title not in subtopics_icons:
            subtopics_icons[subtopic.topic_title] = {}
        subtopics_icons[subtopic.topic_title][subtopic.title] = subtopic.pictureLink

    topic_dict: Dict[str, Dict[str, List[UserWord]]] = {}

    for user_word in user_words:
        topic = user_word.word.topic
        subtopic = user_word.word.subtopic

        if topic not in topic_dict:
            topic_dict[topic] = {}
        if subtopic not in topic_dict[topic]:
            topic_dict[topic][subtopic] = []

        topic_dict[topic][subtopic].append(user_word)

    result = []

    for topic, subtopics in topic_dict.items():
        topic_entry = TopicWords(title=topic, subtopics=[])
        unsorted_words = []

        for subtopic, words in subtopics.items():
            pictureLink = subtopics_icons[topic][subtopic]

            if len(words) < 8:
                unsorted_words.extend(words)
            else:
                word_count = len(words)
                progress = round(
                    sum(word.progress for word in words) / (word_count * 4) * 100
                )
                subtopic_word = SubtopicWords(
                    title=subtopic,
                    word_count=word_count,
                    progress=progress,
                    pictureLink=pictureLink,
                )
                topic_entry.subtopics.append(subtopic_word)

        if unsorted_words:
            word_count = len(unsorted_words)
            progress = round(
                sum(word.progress for word in unsorted_words) / (word_count * 4) * 100
            )
            subtopic_word = SubtopicWords(
                title=DEFAULT_SUBTOPIC,
                word_count=word_count,
                progress=progress,
                pictureLink=DEFAULT_SUBTOPIC_ICON,
            )
            topic_entry.subtopics.append(subtopic_word)

        result.append(topic_entry)

    return result


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

    result = []
    subtopic_word_count = {}

    user_words = await user_words_service.get_user_words_by_filter(
        user_id=user.id, topic_title=topic_title
    )

    for user_word in user_words:
        subtopic = user_word.word.subtopic
        if subtopic not in subtopic_word_count:
            subtopic_word_count[subtopic] = 0
        subtopic_word_count[subtopic] += 1

    for user_word in user_words:
        if subtopic_word_count[user_word.word.subtopic] < 8:
            result.append(user_word)

    return result


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
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    await user_words_service.update_progress_word(
        user_id=user.id, words_ids=schema.words_ids
    )
    await user_service.update_learning_days(user.id)
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
        filepath = destination.__str__()

    response = Audio(
        filename=filename,
        extension=extension,
        filepath=filepath,
        uploaded_at=uploaded_at,
    )

    process_audio_task.apply_async((filepath, user.id), countdown=1)

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
    process_youtube_task.apply_async((schema.link, user.id), countdown=1)
    return schema
