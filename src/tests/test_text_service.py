import pytest
from unittest.mock import AsyncMock

from src.services.text_service import TextService


class TestTextService:

    @staticmethod
    @pytest.mark.asyncio
    async def test_remove_spec_chars():
        error_service = AsyncMock()
        text = "hello, my name is uwords! i need 300$ dollars..... for api) #money"
        user_id = 1

        result = await TextService.remove_spec_chars(
            text=text, error_service=error_service, user_id=user_id
        )
        assert result == "hello my name is uwords i need dollars for api money"

    @staticmethod
    @pytest.mark.asyncio
    async def test_remove_stop_words():
        error_service = AsyncMock()
        text = "ну ты это заходи если ну надо тебе"
        user_id = 1

        result = await TextService.remove_stop_words(
            text=text, error_service=error_service, user_id=user_id
        )
        assert result == ["это", "заходи", "тебе"]

    @staticmethod
    @pytest.mark.asyncio
    async def test_norm_words():
        error_service = AsyncMock()
        words = ["меня", "манили", "её", "руки"]
        user_id = 1

        result = await TextService.normalize_words(
            words=words, error_service=error_service, user_id=user_id
        )

        assert result == ["я", "манить", "её", "рука"]

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_frequency_dict():
        error_service = AsyncMock()
        words = ["uwords", "uwords", "uwords", "best", "team"]
        user_id = 1

        result = await TextService.create_freq_dict(
            words=words, error_service=error_service, user_id=user_id
        )
        assert result == {"uwords": 3, "team": 1, "best": 1}

    @staticmethod
    @pytest.mark.asyncio
    async def test_translate_to_english():
        error_service = AsyncMock()
        words = {"привет": 1, "погода": 1, "сегодня": 1, "прекрасный": 2, "очень": 1}
        user_id = 1

        result = await TextService.translate(
            words=words,
            from_lang="russian",
            to_lang="english",
            error_service=error_service,
            user_id=user_id,
        )
        assert result == [
            {"enValue": "Hello", "ruValue": "Привет", "frequency": 1},
            {"enValue": "Weather", "ruValue": "Погода", "frequency": 1},
            {"enValue": "Today", "ruValue": "Сегодня", "frequency": 1},
            {"enValue": "Beautiful", "ruValue": "Прекрасный", "frequency": 2},
            {"enValue": "Very", "ruValue": "Очень", "frequency": 1},
        ]

    @staticmethod
    @pytest.mark.asyncio
    async def test_translate_to_russian():
        error_service = AsyncMock()
        words = {"laptop": 3, "fell": 1, "crashed": 1}
        user_id = 1

        result = await TextService.translate(
            words=words,
            from_lang="english",
            to_lang="russian",
            error_service=error_service,
            user_id=user_id,
        )
        assert result == [
            {"enValue": "Laptop", "ruValue": "Ноутбук", "frequency": 3},
            {"enValue": "Fell", "ruValue": "Упал", "frequency": 1},
            {"enValue": "Crashed", "ruValue": "Разбился", "frequency": 1},
        ]
