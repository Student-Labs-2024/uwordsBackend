import os
from typing import Dict
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
from src.services.payment_service import PaymentService
from src.services.subscription_service import SubscriptionService

from src.services.user_service import UserService
from src.services.word_service import WordService
from src.services.topic_service import TopicService
from src.services.user_word_service import UserWordService
from src.services.user_achievement_service import UserAchievementService
from src.services.user_word_stop_list_service import UserWordStopListService

from src.utils.metric import send_user_data
from src.utils.helpers import get_allowed_iterations_and_metric_data
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.word_service_fabric import word_service_fabric
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric
from src.utils.dependenes.payment_service_fabric import payment_service_fabric
from src.utils.dependenes.chroma_service_fabric import subtopic_service_fabric
from src.utils.dependenes.user_achievement_fabric import user_achievement_service_fabric
from src.utils.dependenes.user_word_stop_list_service_fabric import (
    user_word_stop_list_service_fabric,
)
from src.utils.logger import celery_tasks_logger


@app.task(bind=True, name="Email_send", max_retries=2)
def send_email_task(self, email: str, code: str):
    EmailService.send_email(
        email=email, theme="Uwords - Confirmation Code", text=f"Your code is {code}"
    )


@app.task(bind=True, name="check_payment", max_retries=1440)
def auto_check_payment_task(self, user_id: int, pay_id: str):
    try:
        result = async_to_sync(auto_check_payment)(user_id=user_id, pay_id=pay_id)

        status = result.get("status")
        message = result.get("message")

        if status == 200:
            return "Подписка оплачена!"

        elif status == 202:
            raise self.retry(countdown=60)

        else:
            return message

    except MaxRetriesExceededError:
        return "Время действия ссылки истёк!"


@app.task(bind=True, name="process_youtube", max_retries=2)
def process_youtube_task(self, link: str, user_id: int):
    try:
        result = async_to_sync(process_youtube)(link=link, user_id=user_id)

        if not result:
            raise self.retry(countdown=1)

        if result == "Not found":
            return "Счёт не найден"

        return "Загрузка видео окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки видео"


@app.task(bind=True, name="process_text", max_retries=2)
def process_text_task(self, text: str, user_id: int):
    try:
        result = async_to_sync(process_text)(text=text, user_id=user_id)

        if not result:
            raise self.retry(countdown=1)

        return "Загрузка текста окончена"

    except MaxRetriesExceededError:
        return "Возникла ошибка загрузки текста"


async def auto_check_payment(
    user_id: int,
    pay_id: str,
    user_service: UserService = user_service_fabric(),
    payment_service: PaymentService = payment_service_fabric(),
    sub_service: SubscriptionService = sub_service_fabric(),
) -> Dict[str, int]:
    user = await user_service.get_user_by_id(user_id=user_id)

    if not user:
        return {"status": 404, "message": "User not found"}

    if not await payment_service.check_payment(label_id=pay_id):
        return {"status": 202, "message": "Waiting"}

    bill = await payment_service.get_bill(pay_id=pay_id)

    if not bill:
        return {"status": 404, "message": "Bill not found"}

    if bill.success:
        return {"status": 200, "message": "Success"}

    subscription = await sub_service.get_sub_by_id(id=bill.sub_type)

    if not subscription:
        return {"status": 404, "message": "Sub not found"}

    await payment_service.update_bill_success(bill_id=bill.id)

    now = datetime.now()
    expired_at = now + relativedelta(months=subscription.months)

    if subscription.free_period_days:
        expired_at += relativedelta(days=subscription.free_period_days)

    await user_service.update_user(
        user_id=user.id,
        user_data={
            "subscription_acquisition": now,
            "subscription_expired": expired_at,
            "subscription_type": bill.sub_type,
        },
    )

    return {"status": 200, "message": "Success"}


async def process_youtube(
    link: str,
    user_id: int,
    error_service: ErrorService = error_service_fabric(),
):
    celery_tasks_logger.info(f"[YOUTUBE UPLOAD] Upload started...")

    file_path, title = await AudioService.upload_youtube_audio(
        link=link, error_service=error_service, user_id=user_id
    )

    return await general_process_audio(
        file_path=file_path.__str__(), type="video", title=title, user_id=user_id
    )


@app.task(bind=True, name="process_audio", max_retries=2)
def process_audio_task(self, path: str, title: str, user_id: int):
    celery_tasks_logger.info(f"[PROCESS AUDIO TASK] Processing file at path: {path}")
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
    user_achievement_service: UserAchievementService = user_achievement_service_fabric(),
    user_word_stop_list_service: UserWordStopListService = user_word_stop_list_service_fabric(),
):
    celery_tasks_logger.info(
        f"[GENERAL PROCESS AUDIO] Processing file at path: {file_path}"
    )

    try:
        files_paths = [file_path]
        user = await user_service.get_user_by_id(user_id=user_id)

        extension = file_path.split(".")[-1]

        if extension != "wav":
            converted_file = await AudioService.convert_audio(
                path=file_path,
                title=title,
                error_service=error_service,
                user_id=user_id,
            )

            files_paths.append(converted_file)

        else:
            converted_file = file_path

        celery_tasks_logger.info(f"[GENERAL PROCESS AUDIO] files_paths: {files_paths}")
        celery_tasks_logger.info(
            f"[GENERAL PROCESS AUDIO] converted_file: {converted_file}"
        )

        duration = get_duration(path=converted_file)

        allowed_iterations, user_data, metric_data = (
            await get_allowed_iterations_and_metric_data(
                type=type, user=user, duration=int(duration)
            )
        )

        if user_data:
            await user_service.update_user(user_id=user.id, user_data=user_data)

        await send_user_data(data=metric_data, server_url=METRIC_URL)

        await user_service.check_user_achievemets(
            user_id=user_id,
            user_achievement_service=user_achievement_service,
        )

        if allowed_iterations == 0:
            celery_tasks_logger.info("[GENERAL PROCESS AUDIO] Seconds limits ran out")
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
                celery_tasks_logger.error(f"[STT RU] Error {e}")

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
                celery_tasks_logger.error(f"[STT EN] Error {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[STT EN] ERROR", description=str(e)
                )

                await error_service.add_one(error=error)

        text_ru = " ".join(result for result in results_ru if result.strip())
        text_en = " ".join(result for result in results_en if result.strip())

        if len(text_ru) == 0 and len(text_en) == 0:
            return False

        if len(text_ru) > len(text_en):
            text = text_ru
        else:
            text = text_en

        celery_tasks_logger.info(f"[GENERAL PROCESS AUDIO] Recognized text: {text}")

        # for file_path in files_paths:
        #     try:
        #         os.remove(path=file_path)
        #     except:
        #         continue

        translated_words = await TextService.get_translated_clear_text(
            text, error_service, user_id
        )
        await user_word_service.upload_user_words(
            user_words=translated_words,
            user_id=user_id,
            uwords_uid=user.uwords_uid,
            word_service=word_service,
            subtopic_service=subtopic_service,
            error_service=error_service,
            user_achievement_service=user_achievement_service,
            user_service=user_service,
            user_word_stop_list_service=user_word_stop_list_service,
        )

        celery_tasks_logger.info(
            f"[GENERAL PROCESS AUDIO] Processing ended successfully!"
        )
        return True
    except Exception as e:
        celery_tasks_logger.error(f"[GENERAL PROCESS AUDIO] Error: {e}")
        return False


async def process_text(
    text: str,
    user_id: int,
    user_service: UserService = user_service_fabric(),
    user_word_service: UserWordService = user_word_service_fabric(),
    word_service: WordService = word_service_fabric(),
    subtopic_service: TopicService = subtopic_service_fabric(),
    error_service: ErrorService = error_service_fabric(),
    user_achievement_service: UserAchievementService = user_achievement_service_fabric(),
    user_word_stop_list_service: UserWordStopListService = user_word_stop_list_service_fabric(),
):
    try:
        user = await user_service.get_user_by_id(user_id=user_id)
        translated_words = await TextService.get_translated_clear_text(
            text=text, error_service=error_service, user_id=user_id
        )
        await user_word_service.upload_user_words(
            user_words=translated_words,
            user_id=user_id,
            uwords_uid=user.uwords_uid,
            word_service=word_service,
            subtopic_service=subtopic_service,
            error_service=error_service,
            user_achievement_service=user_achievement_service,
            user_service=user_service,
            user_word_stop_list_service=user_word_stop_list_service,
        )

        celery_tasks_logger.info(f"[PROCESS Text] Processing ended successfully!")
        return True
    except Exception as e:
        celery_tasks_logger.error(f"[PROCESS Text] Error: {e}")
        return False
