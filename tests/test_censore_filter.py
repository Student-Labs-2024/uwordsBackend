import pytest
from unittest.mock import patch
from src.services.censore_service import CensoreFilter


class TestCensoreFilter:
    @staticmethod
    @pytest.mark.parametrize(
        "text, swear_check_result, profanity_result, expected_result",
        [
            ("Это чистый текст", False, False, False),
            ("Этот текст содержит нецензурное слово", True, False, True),
            ("Another text with profanity", False, True, True),
            ("This text is also clean", False, False, False),
        ],
    )
    @patch("src.services.services_config.swear_check.predict")
    @patch("src.services.services_config.profanity.contains_profanity")
    def test_is_censore(
        mock_profanity,
        mock_swear_check,
        text,
        swear_check_result,
        profanity_result,
        expected_result,
    ):
        mock_swear_check.return_value = [swear_check_result]
        mock_profanity.return_value = profanity_result

        result = CensoreFilter.is_censore(text)
        assert result == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        "text, replRU, replEN, expected_result",
        [
            ("Это чистый текст", "****", "*", "Это чистый текст"),
            (
                "Этот текст содержит нецензурное слово",
                "****",
                "*",
                "Этот текст содержит **** слово",
            ),
            ("This text is also clean", "****", "*", "This text is also clean"),
            ("This text contains a profanity", "****", "*", "This text contains a *"),
        ],
    )
    @patch("src.services.services_config.profanity.censor")
    @patch("src.services.services_config.swear_check.predict")
    def test_replace(
        mock_swear_check, mock_profanity, text, replRU, replEN, expected_result
    ):
        if "нецензурное" in text:
            mock_swear_check.return_value = [False]
            mock_profanity.return_value = text.replace("нецензурное", replRU)
        elif "profanity" in text:
            mock_swear_check.return_value = [False]
            mock_profanity.return_value = text.replace("profanity", replEN)
        else:
            mock_swear_check.return_value = [False]
            mock_profanity.return_value = text

        result = CensoreFilter.replace(text, replRU, replEN)
        assert result == expected_result
