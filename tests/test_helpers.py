from fastapi import HTTPException
import pytest

from src.utils.helpers import check_mime_type, check_youtube_link


class TestCheckMineType:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "filename, result",
        [
            ("valid_file.ogg", True),
            ("valid_file.wav", True),
            ("valid_file.mp3", True),
        ],
    )
    async def test_check_mine_type_success(filename, result):
        bool = await check_mime_type(filename)
        assert bool == result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "filename",
        [
            "invalid_file.jpg",
            "invalid_file.mp4",
            "invalid_file.json",
        ],
    )
    async def test_check_mine_type_failure(filename):
        with pytest.raises(HTTPException):
            await check_mime_type(filename)


class TestCheckYoutubeLink:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "link",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3m25s",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLg9dDJQ5jQfej_z6N6bVYD6Hb-lSbTc_q",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&index=2&list=PLg9dDJQ5jQfej_z6N6bVYD6Hb-lSbTc_q",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=sAQA",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=iAQB",
        ],
    )
    async def test_check_youtube_link_success(link):
        result = await check_youtube_link(link)
        assert result is True

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "link",
        [
            "https://www.youtube.com/watch?v=invalid_video_id",
            "https://www.youtube.com/",
            "https://www.youtube.com/playlist?list=WL",
        ],
    )
    async def test_check_youtube_link_failure(link):
        with pytest.raises(HTTPException):
            await check_youtube_link(link)
