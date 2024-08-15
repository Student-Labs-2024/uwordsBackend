import string
import pytest

from src.utils.email import (
    generate_email_verification_code,
    generate_telegram_verification_code,
)


class TestEmail:
    @staticmethod
    @pytest.mark.parametrize("length", [4, 6, 8])
    def test_generate_email_verification_code(length):
        code = generate_email_verification_code(length)
        assert len(code) == length
        assert all(char in string.digits for char in code)

    @staticmethod
    @pytest.mark.parametrize("length", [4, 6, 8])
    def test_generate_telegram_verification_code(length):
        code = generate_telegram_verification_code(length)
        assert len(code) == length
        assert all(char in string.ascii_letters + string.digits for char in code)
