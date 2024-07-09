import os
import asyncio
import logging
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor
from celery.exceptions import MaxRetriesExceededError

from src.config.celery_app import app
from src.schemes.schemas import ErrorCreate
from src.services.audio_service import AudioService
from src.services.text_service import TextService
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.word_service_fabric import word_service_fabric

logger = logging.getLogger("[CELERY TASKS WORDS]")
logging.basicConfig(level=logging.INFO)


@app.task(bind=True, name="upload_audio", max_retries=2)
def upload_audio_task(self, path: str, user_id: str):
    try:
        result = upload_audio(path=path, user_id=user_id)

        if not result:
            raise self.retry(countdown=5)

        return 'Загрузка аудио окончена'

    except MaxRetriesExceededError:
        return 'Возникла ошибка загрузки аудио'


@app.task(bind=True, name="upload_video", max_retries=2)
def upload_youtube_task(self, link: str, user_id: str):
    try:
        result = upload_youtube(link=link, user_id=user_id)

        if not result:
            raise self.retry(countdown=1)

        return 'Загрузка видео окончена'

    except MaxRetriesExceededError:
        return 'Возникла ошибка загрузки видео'


def upload_youtube(link: str, user_id: str):
    user_word_service = user_word_service_fabric()
    word_service = word_service_fabric()
    subtopic_service = subtopic_service_fabric()
    error_service = error_service_fabric()
    try:
        logger.info(f'[YOUTUBE UPLOAD] Upload started...')

        path, audio_title, video_title = AudioService.upload_youtube_audio(link=link, error_service=error_service, user_id=user_id)

        logger.info(f'PATH: {path}')

        title = f'{os.path.splitext(audio_title)[0]}_converted.wav'

        logger.info(f'TITLE: {title}')

        filepath = AudioService.convert_audio(path=path, title=title, error_service=error_service, user_id=user_id)

        files_paths = []
        files_paths = AudioService.cut_audio(path=filepath, error_service=error_service, user_id=user_id)

        lang = detect(video_title)

        if lang == 'ru':
            with ThreadPoolExecutor(max_workers=20) as executor:
                try:
                    results = list(executor.map(AudioService.speech_to_text_ru, files_paths))
                except Exception as e:
                    logger.info(f'[STT RU] Error {e}')

                    error = ErrorCreate(
                        user_id=user_id,
                        message="[STT RU] ERROR",
                        description=str(e)
                    )

                    asyncio.run(error_service.add_one(error=error))
                
        else:
            with ThreadPoolExecutor(max_workers=20) as executor:
                try:
                    results = list(executor.map(AudioService.speech_to_text_en, files_paths))
                except Exception as e:
                    logger.info(f'[STT EN] Error {e}')

                    error = ErrorCreate(
                        user_id=user_id,
                        message="[STT EN] ERROR",
                        description=str(e)
                    )

                    asyncio.run(error_service.add_one(error=error))

        freq_dict = TextService.get_frequency_dict(text=' '.join(results), error_service=error_service, user_id=user_id)

        if lang == 'ru':
            translated_words = TextService.translate(words=freq_dict, from_lang="russian", to_lang="english", error_service=error_service, user_id=user_id)
        else:
            translated_words = TextService.translate(words=freq_dict, from_lang="english", to_lang="russian", error_service=error_service, user_id=user_id)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            user_word_service.upload_user_words(
                user_words=translated_words,
                user_id=user_id,
                word_service=word_service,
                subtopic_service=subtopic_service,
                error_service=error_service
                )
            )

        logger.info(f'[YOUTUBE UPLOAD] Upload ended successfully!')

        return True

    except BaseException as e:
        logger.info(f'[YOUTUBE UPLOAD] Error occured {e}')
        error = ErrorCreate(
            user_id=user_id,
            message="[YOUTUBE UPLOAD] ERROR",
            description=str(e)
        )

        asyncio.run(error_service.add_one(error=error))
        return False

    finally:
        for file_path in files_paths + [path, filepath]:
            try:
                os.remove(path=file_path)
            except:
                continue


def upload_audio(path: str, user_id: str):
    user_word_service = user_word_service_fabric()
    word_service = word_service_fabric()
    subtopic_service = subtopic_service_fabric()
    error_service = error_service_fabric()
    try:

        logger.info(f'[AUDIO UPLOAD] {path}')

        files_paths = []
        files_paths = AudioService.cut_audio(path=path, error_service=error_service, user_id=user_id)

        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_ru = list(executor.map(AudioService.speech_to_text_ru, files_paths))
            except Exception as e:
                logger.info(f'[STT RU] Error {e}')

                error = ErrorCreate(
                    user_id=user_id,
                    message="[STT RU] ERROR",
                    description=str(e)
                )

                asyncio.run(error_service.add_one(error=error))
            
        with ThreadPoolExecutor(max_workers=20) as executor:
            try:
                results_en = list(executor.map(AudioService.speech_to_text_en, files_paths))
            
            except Exception as e:
                logger.info(f'[STT EN] Error {e}')

                error = ErrorCreate(
                    user_id=user_id,
                    message="[STT EN] ERROR",
                    description=str(e)
                )

                asyncio.run(error_service.add_one(error=error))

        if len(' '.join(results_ru)) > len(' '.join(results_en)):
            is_ru = True
            results = results_ru

        else:
            is_ru = False
            results = results_en

        freq_dict = TextService.get_frequency_dict(text=' '.join(results), error_service=error_service, user_id=user_id)

        if is_ru:
            translated_words = TextService.translate(words=freq_dict, from_lang="russian", to_lang="english", error_service=error_service, user_id=user_id)
        else:
            translated_words = TextService.translate(words=freq_dict, from_lang="english", to_lang="russian", error_service=error_service, user_id=user_id)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            user_word_service.upload_user_words(
                user_words=translated_words,
                user_id=user_id,
                word_service=word_service,
                subtopic_service=subtopic_service,
                error_service=error_service
            )
        )

        logger.info(f'[AUDIO UPLOAD] Upload ended successfully!')

        return True

    except Exception as e:
        logger.info(f'[AUDIO UPLOAD] Error occured! {e}')
        error = ErrorCreate(
            user_id=user_id,
            message="[AUDIO UPLOAD] ERROR",
            description=str(e)
        )

        asyncio.run(error_service.add_one(error=error))
        return False

    finally:
        for file_path in files_paths + [path]:
            try:
                os.remove(path=file_path)
            except:
                continue