import os
import uuid
import logging
from pydub import AudioSegment
from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, File, UploadFile, Depends
from src.config.instance import UPLOAD_DIR
from src.database.models import UserWord
from src.schemes.schemas import Audio, UserWordDumpSchema, WordsIdsSchema, YoutubeLink
from src.services.error_service import ErrorService
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.file_service_fabric import file_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.services.audio_service import AudioService
from src.services.file_service import FileService
from src.services.user_word_service import UserWordService
from src.celery.tasks import upload_audio_task, upload_youtube_task

user_router_v1 = APIRouter(prefix="/api/v1/user")

logger = logging.getLogger("[ROUTER WORDS]")
logging.basicConfig(level=logging.INFO)


# response_model=List[UserWordDumpSchema]
@user_router_v1.get("/words/get_words", tags=["User Words"])
async def get_user_words(user_id: str,
                         user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)]):
    user_words: List[UserWord] = await user_words_service.get_user_words(user_id)
    words = [x.word for x in user_words]
    subtopics = {}
    topics = []
    subtopics_words = {}
    non_subtopics_words = []
    for word in words:
        if word.topic not in topics:
            topics.append(word.topic)
        if word.subtopic not in subtopics:
            subtopics[word.subtopic] = 1
        else:
            subtopics[word.subtopic] += 1
    for word in words:
        add_word = {
            "ruValue": word.ruValue,
            "enValue": word.enValue,
            "id": word.id,
            "pictureLink": word.pictureLink,
            "audioLink": word.audioLink
        }
        if word.subtopic not in subtopics_words:
            if word.subtopic in subtopics:
                if subtopics[word.subtopic] >= 8:
                    subtopics_words[word.subtopic] = [add_word]
                else:
                    non_subtopics_words.append(add_word)
        else:
            subtopics_words[word.subtopic].append(add_word)
    result = []
    for topic in topics:
        topic_dump = {
            'topic': topic,
            'words_in_subtopics': subtopics_words,
            'words_without_subtopic': non_subtopics_words
        }
        result.append(topic_dump)
    return result


@user_router_v1.get("/words/study", response_model=List[UserWordDumpSchema], tags=["User Words"])
async def get_user_words_for_study(user_id: str,
                                   user_words_service: Annotated[UserWordService, Depends(user_word_service_fabric)],
                                   topic_id: int | None = None):
    words_for_study = await user_words_service.get_user_words_for_study(user_id=user_id, topic_id=topic_id)

    return words_for_study


@user_router_v1.post("/words/study", response_model=WordsIdsSchema, tags=["User Words"])
async def complete_user_words_learning(user_id: str, schema: WordsIdsSchema, user_words_service: Annotated[
    UserWordService, Depends(user_word_service_fabric)]):
    await user_words_service.update_progress_word(user_id=user_id, words_ids=schema.words_ids)
    return schema


@user_router_v1.post("/audio", response_model=Audio, tags=["User Words"])
async def upload_audio(
        user_id: str,
        file: Annotated[UploadFile, File(description="A file read as UploadFile")],
        file_service: Annotated[FileService, Depends(file_service_fabric)],
        error_service: Annotated[ErrorService, Depends(error_service_fabric)],

) -> Audio:
    filename = file.filename
    _, extension = os.path.splitext(filename)
    uploaded_at = datetime.now()

    filedata = await file.read()

    audio_name = f'audio_{uuid.uuid4()}{extension}'
    destination = UPLOAD_DIR / audio_name

    try:
        await file_service.add_file(destination, filedata)

        duration = int(len(AudioSegment.from_file(file=destination)) / 1000)

        logger.info(f'DURATION: {duration}')

    except Exception as e:
        logger.info(e)

    if extension != ".wav":
        title = f'{os.path.splitext(audio_name)[0]}_converted.wav'
        filepath = AudioService.convert_audio(path=destination, title=title, error_service=error_service, user_id=user_id)
        await file_service.delete_file(destination)

    else:
        filepath = destination

    response = Audio(
        filename=filename,
        extension=extension,
        filepath=filepath,
        uploaded_at=uploaded_at,
    )

    upload_audio_task.apply_async((filepath, user_id), countdown=1)

    return response


@user_router_v1.post("/youtube", response_model=YoutubeLink, tags=["User Words"])
async def upload_youtube_video(user_id: str, schema: YoutubeLink):
    upload_youtube_task.apply_async((schema.link, user_id,), countdown=1)
    return schema
