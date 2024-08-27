import re
import logging
import mimetypes
from typing import Dict, Tuple

from fastapi import HTTPException, status

from src.config.instance import (
    ALLOWED_AUDIO_MIME_TYPES,
    ALLOWED_YOUTUBE_LINK_PATTERNS,
    ALLOWED_ICON_MIME_TYPES,
)
from src.database.models import User


logger = logging.getLogger("[HELPERS]")
logging.basicConfig(level=logging.INFO)


async def check_mime_type(filename: str) -> bool:
    logger.info(f"[MIMETYPE AUDIO] Filename: {filename}")

    mime_type = mimetypes.guess_type(filename)[0]

    if mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        logger.info(
            f"[MIMETYPE AUDIO] Error: Invalid file extension: {mime_type!r}. Expected: {ALLOWED_AUDIO_MIME_TYPES!r}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Invalid file extension: {mime_type!r}. Expected: {ALLOWED_AUDIO_MIME_TYPES!r}"
            },
        )

    return True


async def check_mime_type_icon(filename: str) -> str:
    logger.info(f"[MIMETYPE ICON] Filename: {filename}")

    mime_type = mimetypes.guess_type(filename)[0]

    if mime_type not in ALLOWED_ICON_MIME_TYPES:
        logger.info(
            f"[MIMETYPE ICON] Error: Invalid file extension: {mime_type!r}. Expected: {ALLOWED_ICON_MIME_TYPES!r}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Invalid file extension: {mime_type!r}. Expected: {ALLOWED_ICON_MIME_TYPES!r}"
            },
        )

    return mime_type


async def check_youtube_link(link: str) -> bool:

    logger.info(f"[YOUTUBE] Link: {link}")

    for pattern in ALLOWED_YOUTUBE_LINK_PATTERNS:
        if re.match(pattern, link):
            return True

    logger.info(f"[YOUTUBE] Error: Invalid URL: {link}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Invalid URL"}
    )


async def get_allowed_iterations_and_metric_data(
    type: str, user: User, duration: int
) -> Tuple[int, Dict, Dict]:
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

            user_data = {"allowed_audio_seconds": allowed_audio_seconds}

            metric_data = {"uwords_uid": user.uwords_uid, "speech_seconds": duration}

        else:
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

            user_data = {"allowed_video_seconds": allowed_video_seconds}

            metric_data = {
                "uwords_uid": user.uwords_uid,
                "video_seconds": metric_duration,
            }

    else:
        if type == "audio":
            metric_data = {
                "uwords_uid": user.uwords_uid,
                "speech_seconds": metric_duration,
            }
        else:
            metric_data = {
                "uwords_uid": user.uwords_uid,
                "video_seconds": metric_duration,
            }

        allowed_iterations = None

    return allowed_iterations, user_data, metric_data
