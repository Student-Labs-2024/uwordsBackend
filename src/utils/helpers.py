import re
import mimetypes

from fastapi import HTTPException, status, UploadFile

from src.config.instance import ALLOWED_AUDIO_MIME_TYPES, ALLOWED_YOUTUBE_LINK_PATTERNS


async def check_mime_type(file: UploadFile) -> bool:
    mime_type = mimetypes.guess_type(url=file.filename)[0]

    if mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": f"Invalid file extension: {mime_type!r}. Expected: {ALLOWED_AUDIO_MIME_TYPES!r}"
            },
        )

    return True


async def check_youtube_link(link: str) -> bool:

    for pattern in ALLOWED_YOUTUBE_LINK_PATTERNS:
        if re.match(pattern, link):
            return True

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Invalid URL"}
    )
