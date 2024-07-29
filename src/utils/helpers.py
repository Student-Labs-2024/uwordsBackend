import re
import mimetypes

from fastapi import HTTPException, status

from src.config.instance import (
    ALLOWED_AUDIO_MIME_TYPES,
    ALLOWED_YOUTUBE_LINK_PATTERNS,
    ALLOWED_ICON_MIME_TYPES,
)


async def check_mime_type(filename: str) -> bool:
    mime_type = mimetypes.guess_type(filename)[0]

    if mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Invalid file extension: {mime_type!r}. Expected: {ALLOWED_AUDIO_MIME_TYPES!r}"
            },
        )

    return True


async def check_mime_type_icon(filename: str) -> str:
    mime_type = mimetypes.guess_type(filename)[0]

    if mime_type not in ALLOWED_ICON_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Invalid file extension: {mime_type!r}. Expected: {ALLOWED_ICON_MIME_TYPES!r}"
            },
        )

    return mime_type


async def check_youtube_link(link: str) -> bool:

    for pattern in ALLOWED_YOUTUBE_LINK_PATTERNS:
        if re.match(pattern, link):
            return True

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Invalid URL"}
    )
