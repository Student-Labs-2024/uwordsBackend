import os
import asyncio
import logging
from langdetect import detect
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
from celery.exceptions import MaxRetriesExceededError

from src.config.celery_app import app

from src.schemes.schemas import ErrorCreate

from src.services.text_service import TextService
from src.services.audio_service import AudioService
from src.services.email_service import EmailService
from src.services.error_service import ErrorService

from src.services.word_service import WordService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService

from src.utils.dependenes.word_service_fabric import word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric


logger = logging.getLogger("[CELERY TASKS WORDS]")
logging.basicConfig(level=logging.INFO)


@app.task(bind=True, name="Email_send", max_retries=2)
def send_email_task(self, email: str, code: str):
    EmailService.send_email(email=email, code=code)


@app.task(bind=True, name="upload_video", max_retries=2)
def upload_youtube_task(self, link: str, user_id: int):
    try:
        result = async_to_sync(upload_youtube)(link=link, user_id=user_id)

        if not result:
            raise self.retry(countdown=1)

        return "Загрузка видео окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки видео"


async def upload_youtube(
    link: str,
    user_id: int,
    user_word_service: UserWordService = user_word_service_fabric(),
    word_service: WordService = word_service_fabric(),
    subtopic_service: TopicService = subtopic_service_fabric(),
    error_service: ErrorService = error_service_fabric(),
):
    try:
        logger.info(f"[YOUTUBE UPLOAD] Upload started...")

        files_paths = []
        path, audio_title, video_title = await AudioService.upload_youtube_audio(
            link=link, error_service=error_service, user_id=user_id
        )

        logger.info(f"PATH: {path}")

        title = f"{os.path.splitext(audio_title)[0]}_converted.wav"

        logger.info(f"TITLE: {title}")

        filepath = await AudioService.convert_audio(
            path=path, title=title, error_service=error_service, user_id=user_id
        )

        files_paths = await AudioService.cut_audio(
            path=filepath, error_service=error_service, user_id=user_id
        )

        lang = detect(video_title)

        if lang == "ru":
            with ThreadPoolExecutor(max_workers=20) as executor:
                try:
                    results = list(
                        executor.map(AudioService.speech_to_text_ru, files_paths)
                    )
                except Exception as e:
                    logger.info(f"[STT RU] Error {e}")

                    error = ErrorCreate(
                        user_id=user_id, message="[STT RU] ERROR", description=str(e)
                    )

                    await error_service.add_one(error=error)

        else:
            with ThreadPoolExecutor(max_workers=20) as executor:
                try:
                    results = list(
                        executor.map(AudioService.speech_to_text_en, files_paths)
                    )
                except Exception as e:
                    logger.info(f"[STT EN] Error {e}")

                    error = ErrorCreate(
                        user_id=user_id, message="[STT EN] ERROR", description=str(e)
                    )

                    await error_service.add_one(error=error)

        text = " ".join(results)

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

        if lang == "ru":
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

        logger.info(f"[YOUTUBE UPLOAD] Upload ended successfully!")

        return True

    except BaseException as e:
        logger.info(f"[YOUTUBE UPLOAD] Error occured {e}")

        error = ErrorCreate(
            user_id=user_id, message="[YOUTUBE UPLOAD] ERROR", description=str(e)
        )

        await error_service.add_one(error=error)
        return False

    finally:
        for file_path in files_paths + [path, filepath]:
            try:
                os.remove(path=file_path)
            except:
                continue


@app.task(bind=True, name="upload_audio", max_retries=2)
def upload_audio_task(self, path: str, user_id: int):
    try:
        result = async_to_sync(upload_audio)(path=path, user_id=user_id)

        if not result:
            raise self.retry(countdown=5)

        return "Загрузка аудио окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки аудио"


async def upload_audio(
    path: str,
    user_id: int,
    user_word_service: UserWordService = user_word_service_fabric(),
    word_service: WordService = word_service_fabric(),
    subtopic_service: TopicService = subtopic_service_fabric(),
    error_service: ErrorService = error_service_fabric(),
):
    try:

        logger.info(f"[AUDIO UPLOAD] {path}")

        files_paths = []
        files_paths = await AudioService.cut_audio(
            path=path, error_service=error_service, user_id=user_id
        )

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_ru = list(
                    executor.map(AudioService.speech_to_text_ru, files_paths)
                )
            except Exception as e:
                logger.info(f"[STT RU] Error {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[STT RU] ERROR", description=str(e)
                )

                asyncio.run(error_service.add_one(error=error))

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_en = list(
                    executor.map(AudioService.speech_to_text_en, files_paths)
                )

            except Exception as e:
                logger.info(f"[STT EN] Error {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[STT EN] ERROR", description=str(e)
                )

                await error_service.add_one(error=error)

        if len(" ".join(results_ru)) > len(" ".join(results_en)):
            is_ru = True
            results = results_ru

        else:
            is_ru = False
            results = results_en

        text = " ".join(results)

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

        if is_ru:
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

        logger.info(f"[AUDIO UPLOAD] Upload ended successfully!")

        return True

    except Exception as e:
        logger.info(f"[AUDIO UPLOAD] Error occured! {e}")
        error = ErrorCreate(
            user_id=user_id, message="[AUDIO UPLOAD] ERROR", description=str(e)
        )

        await error_service.add_one(error=error)
        return False

    finally:
        for file_path in files_paths + [path]:
            try:
                os.remove(path=file_path)
            except:
                continue
