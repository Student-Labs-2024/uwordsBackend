import logging
from datetime import datetime
from asgiref.sync import async_to_sync
from dateutil.relativedelta import relativedelta

from src.config.celery_app import app

from src.config.instance import (
    ALLOWED_AUDIO_SECONDS,
    ALLOWED_VIDEO_SECONDS,
    DEFAULT_ENERGY,
)
from src.database.models import Subscription
from src.services.subscription_service import SubscriptionService
from src.services.user_service import UserService
from src.services.email_service import EmailService
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.logger import scheduled_tasks_logger


@app.task(name="TestTask")
def test_task():
    scheduled_tasks_logger.info("Ежеминутная задача")


@app.task(name="check_sub")
def check_sub_receiver():
    scheduled_tasks_logger.info("[CHECK SUB] Received")
    async_to_sync(check_sub)()
    scheduled_tasks_logger.info("[CHECK SUB] Completed")


async def check_sub(
    user_service: UserService = user_service_fabric(),
    sub_service: SubscriptionService = sub_service_fabric(),
):
    users = await user_service.get_users_with_sub()

    for user in users:
        sub: Subscription = await sub_service.get_sub_by_id(name=user.subscription_type)

        date: datetime = user.subscription_acquisition

        if date + relativedelta(months=sub.months) > datetime.now():
            await user_service.update_user(
                user_id=user.id, user_data={"subscription_type": None}
            )


@app.task(name="reset_limits")
def reset_limits_receiver():
    scheduled_tasks_logger.info("[RESET LIMITS] Received")
    async_to_sync(reset_limits)()
    scheduled_tasks_logger.info("[RESET LIMITS] Completed")


async def reset_limits(user_service: UserService = user_service_fabric()):
    users = await user_service.get_users_without_sub()

    for user in users:
        await user_service.update_user(
            user_id=user.id,
            user_data={
                "allowed_audio_seconds": ALLOWED_AUDIO_SECONDS,
                "allowed_video_seconds": ALLOWED_VIDEO_SECONDS,
                "energy": DEFAULT_ENERGY,
            },
        )


@app.task(name="send_notifications")
def send_notifications_receiver():
    scheduled_tasks_logger.info("[SEND NOTIFICATIONS] Received")
    async_to_sync(send_notifications)()
    scheduled_tasks_logger.info("[SEND NOTIFICATIONS] Completed")


async def send_notifications(user_service: UserService = user_service_fabric()):
    users = await user_service.get_users()

    now = datetime.now()

    for user in users:
        if not user.latest_study:
            continue

        latest_study: datetime = user.latest_study

        time_delta = now - latest_study

        if time_delta.days == 1:
            EmailService.send_email(
                email=user.email,
                theme="Uwords - Stroke Days",
                text=f"Hello, Dear {user.username}!\n\nTime to learn! Otherwise your progress will be reset!",
            )
