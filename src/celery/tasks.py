import os
import asyncio
import logging
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor
from celery.exceptions import MaxRetriesExceededError

from src.config.celery_app import app
from src.services.audio_service import AudioService
from src.services.text_service import TextService
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.word_service_fabric import word_service_fabric

logger = logging.getLogger("[CELERY TASKS WORDS]")
logging.basicConfig(level=logging.INFO)


@app.task(bind=True, name="upload_audio", max_retries=2)
def upload_audio_task(self, path: str, user_id: str):
    user_word_service = user_word_service_fabric()
    word_service = word_service_fabric()
    try:
        result = AudioService.upload_audio(path, user_id, user_word_service, word_service)

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
    try:
        logger.info(f'[YOUTUBE UPLOAD] Upload started...')

        path, audio_title, video_title = AudioService.upload_youtube_audio(link=link)

        logger.info(f'PATH: {path}')

        title = f'{os.path.splitext(audio_title)[0]}_converted.wav'

        logger.info(f'TITLE: {title}')

        filepath = AudioService.convert_audio(path=path, title=title)

        files_paths = []
        files_paths = AudioService.cut_audio(path=filepath)

        lang = detect(video_title)

        if lang == 'ru':
            with ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(AudioService.speech_to_text_ru, files_paths))
        else:
            with ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(AudioService.speech_to_text_en, files_paths))

        freq_dict = TextService.get_frequency_dict(text=' '.join(results))

        if lang == 'ru':
            translated_words = TextService.translate(words=freq_dict, from_lang="russian", to_lang="english")
        else:
            translated_words = TextService.translate(words=freq_dict, from_lang="english", to_lang="russian")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(user_word_service.upload_user_words(translated_words, user_id, word_service))

        logger.info(f'[YOUTUBE UPLOAD] Upload ended successfully!')

        return True

    except BaseException as e:
        logger.info(f'[YOUTUBE UPLOAD] Error occured')
        logger.info(e)
        return False

    finally:
        for file_path in files_paths + [path, filepath]:
            try:
                os.remove(path=file_path)
            except:
                continue
