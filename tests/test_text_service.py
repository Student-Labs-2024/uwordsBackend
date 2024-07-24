import pytest
from unittest.mock import AsyncMock

from src.services.text_service import TextService


class TestTextService:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "text, expected_result",
        [
            (
                "hello, my name is uwords! i need 300$ dollars..... for api) #money",
                "hello my name is uwords i need dollars for api money",
            ),
            ("hello world!", "hello world"),
            ("hi there? how are you?", "hi there how are you"),
            ("what's up?", "whats up"),
        ],
    )
    async def test_remove_spec_chars(text, expected_result):
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.remove_spec_chars(
            text=text, error_service=error_service, user_id=user_id
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "text, expected_result",
        [
            ("ну ты это заходи если ну надо тебе", ["это", "заходи", "тебе"]),
            ("я люблю пиццу", ["люблю", "пиццу"]),
            ("как дела", ["дела"]),
        ],
    )
    async def test_remove_stop_words(text, expected_result):
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.remove_stop_words(
            text=text, error_service=error_service, user_id=user_id
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "words, expected_result",
        [
            (["меня", "манили", "её", "руки"], ["я", "манить", "её", "рука"]),
            (["ходил", "был", "видел"], ["ходить", "быть", "видеть"]),
            (["пишу", "читаю", "слушаю"], ["писать", "читать", "слушать"]),
            (["бежать", "прыгать", "плавать"], ["бежать", "прыгать", "плавать"]),
        ],
    )
    async def test_norm_words(words, expected_result):
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.normalize_words(
            words=words, error_service=error_service, user_id=user_id
        )

        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "words, expected_result",
        [
            (
                ["uwords", "uwords", "uwords", "best", "team"],
                {"uwords": 3, "team": 1, "best": 1},
            ),
            (
                ["hello", "world", "hello", "world", "python"],
                {"hello": 2, "world": 2, "python": 1},
            ),
            (
                ["apple", "banana", "apple", "orange", "banana"],
                {"apple": 2, "banana": 2, "orange": 1},
            ),
            (["cat", "dog", "cat", "dog", "cat"], {"cat": 3, "dog": 2}),
        ],
    )
    async def test_get_frequency_dict(words, expected_result):
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.create_freq_dict(
            words=words, error_service=error_service, user_id=user_id
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "words, expected_result",
        [
            (
                {"привет": 1, "погода": 1, "сегодня": 1, "прекрасный": 2, "очень": 1},
                [
                    {"enValue": "Hello", "ruValue": "Привет", "frequency": 1},
                    {"enValue": "Weather", "ruValue": "Погода", "frequency": 1},
                    {"enValue": "Today", "ruValue": "Сегодня", "frequency": 1},
                    {"enValue": "Beautiful", "ruValue": "Прекрасный", "frequency": 2},
                    {"enValue": "Very", "ruValue": "Очень", "frequency": 1},
                ],
            ),
        ],
    )
    async def test_translate_to_english(words, expected_result):
        from_lang = "russian"
        to_lang = "english"
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.translate(
            words=words,
            from_lang=from_lang,
            to_lang=to_lang,
            error_service=error_service,
            user_id=user_id,
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "words, expected_result",
        [
            (
                {"laptop": 3, "fell": 1, "crashed": 1},
                [
                    {"enValue": "Laptop", "ruValue": "Ноутбук", "frequency": 3},
                    {"enValue": "Fell", "ruValue": "Упал", "frequency": 1},
                    {"enValue": "Crashed", "ruValue": "Разбился", "frequency": 1},
                ],
            ),
        ],
    )
    async def test_translate_to_russian(words, expected_result):
        from_lang = "english"
        to_lang = "russian"
        error_service = AsyncMock()
        user_id = 1

        result = await TextService.translate(
            words=words,
            from_lang=from_lang,
            to_lang=to_lang,
            error_service=error_service,
            user_id=user_id,
        )
        assert result == expected_result
