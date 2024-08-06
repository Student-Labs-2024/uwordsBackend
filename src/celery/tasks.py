import os
import logging
from langdetect import detect
from librosa import get_duration
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
from celery.exceptions import MaxRetriesExceededError

from src.config.celery_app import app

from src.config.instance import METRIC_URL
from src.schemes.error_schemas import ErrorCreate

from src.services.text_service import TextService
from src.services.audio_service import AudioService
from src.services.email_service import EmailService
from src.services.error_service import ErrorService

from src.services.user_service import UserService
from src.services.word_service import WordService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService

from src.utils.metric import send_user_data
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.word_service_fabric import word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric


logger = logging.getLogger("[CELERY TASKS WORDS]")
logging.basicConfig(level=logging.INFO)


@app.task(bind=True, name="Email_send", max_retries=2)
def send_email_task(self, email: str, code: str):
    EmailService.send_email(
        email=email, theme="Uwords - Confirantion Code", text=f"Your code is {code}"
    )


@app.task(bind=True, name="process_youtube", max_retries=2)
def process_youtube_task(self, link: str, user_id: int):
    try:
        result = async_to_sync(process_youtube)(link=link, user_id=user_id)

        if not result:
            raise self.retry(countdown=1)

        return "Загрузка видео окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки видео"


async def process_youtube(
    link: str,
    user_id: int,
    error_service: ErrorService = error_service_fabric(),
):
    logger.info(f"[YOUTUBE UPLOAD] Upload started...")

    file_path, title = await AudioService.upload_youtube_audio(
        link=link, error_service=error_service, user_id=user_id
    )

    await general_process_audio(
        file_path=file_path, type="video", title=title, user_id=user_id
    )


@app.task(bind=True, name="process_audio", max_retries=2)
def process_audio_task(self, path: str, title: str, user_id: int):
    try:
        result = async_to_sync(general_process_audio)(
            file_path=path, type="audio", title=title, user_id=user_id
        )

        if not result:
            raise self.retry(countdown=5)

        return "Загрузка аудио окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки аудио"


async def general_process_audio(
    file_path: str,
    type: str,
    title: str,
    user_id: int,
    user_service: UserService = user_service_fabric(),
    user_word_service: UserWordService = user_word_service_fabric(),
    word_service: WordService = word_service_fabric(),
    subtopic_service: TopicService = subtopic_service_fabric(),
    error_service: ErrorService = error_service_fabric(),
):
    try:
        files_paths = [file_path]
        user = await user_service.get_user_by_id(user_id=user_id)

        converted_file = await AudioService.convert_audio(
            path=file_path, title=title, error_service=error_service, user_id=user_id
        )

        files_paths.append(converted_file)

        duration = get_duration(path=converted_file)

        if not user.subscription_type:
            if type == "audio":
                remained_seconds: int = user.allowed_audio_seconds

                allowed_iterations = remained_seconds // 30

                if remained_seconds % 30 != 0:
                    allowed_iterations += 1

                if remained_seconds - duration < 0:
                    allowed_audio_seconds = 0
                    metric_duration = remained_seconds
                else:
                    metric_duration = duration
                    allowed_audio_seconds = remained_seconds - duration

                await user_service.update_user(
                    user_id=user_id,
                    user_data={"allowed_audio_seconds": allowed_audio_seconds},
                )

                metric_data = {"user_id": user_id, "speech_seconds": duration}

            elif type == "video":
                remained_seconds: int = user.allowed_video_seconds
                allowed_iterations = remained_seconds // 30
                if remained_seconds % 30 != 0:
                    allowed_iterations += 1

                if remained_seconds - duration < 0:
                    allowed_video_seconds = 0
                    metric_duration = remained_seconds
                else:
                    metric_duration = duration
                    allowed_video_seconds = remained_seconds - duration

                await user_service.update_user(
                    user_id=user_id,
                    user_data={"allowed_video_seconds": allowed_video_seconds},
                )

                metric_data = {"user_id": user_id, "video_seconds": metric_duration}

        else:
            metric_data = {"user_id": user_id, "video_seconds": metric_duration}
            allowed_iterations = None

        await send_user_data(data=metric_data, server_url=METRIC_URL)

        if allowed_iterations == 0:
            logger.info("[GENERAL PROCESS AUDIO] Seconds limits ran out")
            return True

        cutted_files = await AudioService.cut_audio(
            path=converted_file,
            error_service=error_service,
            user_id=user_id,
            duration=duration,
            allowed_iterations=allowed_iterations,
        )

        files_paths += cutted_files

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_ru = list(
                    executor.map(AudioService.speech_to_text_ru, cutted_files)
                )
            except Exception as e:
                logger.info(f"[STT RU] Error {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[STT RU] ERROR", description=str(e)
                )

                await error_service.add_one(error=error)

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_en = list(
                    executor.map(AudioService.speech_to_text_en, cutted_files)
                )

            except Exception as e:
                logger.info(f"[STT EN] Error {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[STT EN] ERROR", description=str(e)
                )

                await error_service.add_one(error=error)

        if len(" ".join(results_ru)) > len(" ".join(results_en)):
            text = " ".join(results_ru)
        else:
            text = " ".join(results_en)

        logger.info(text)

        text_language = detect(text=text)

        text_without_spec_chars = await TextService.remove_spec_chars(
            text=text, error_service=error_service, user_id=user_id
        )

        words = await TextService.remove_stop_words(
            text=text_without_spec_chars,
            error_service=error_service,
            user_id=user_id,
        )

        norm_words = await TextService.normalize_words(
            words=words, error_service=error_service, user_id=user_id
        )

        freq_dict = await TextService.create_freq_dict(
            words=norm_words, error_service=error_service, user_id=user_id
        )

        if text_language == "ru":
            translated_words = await TextService.translate(
                words=freq_dict,
                from_lang="russian",
                to_lang="english",
                error_service=error_service,
                user_id=user_id,
            )

        else:
            translated_words = await TextService.translate(
                words=freq_dict,
                from_lang="english",
                to_lang="russian",
                error_service=error_service,
                user_id=user_id,
            )

        await user_word_service.upload_user_words(
            user_words=translated_words,
            user_id=user_id,
            word_service=word_service,
            subtopic_service=subtopic_service,
            error_service=error_service,
        )

        logger.info(f"[GENERAL PROCESS AUDIO] Processing ended successfully!")
        return True
    except Exception as e:
        logger.info(f"[GENERAL PROCESS AUDIO] Error: {e}")
        return False
    finally:
        for file_path in files_paths:
            try:
                os.remove(path=file_path)
            except:
                continue
