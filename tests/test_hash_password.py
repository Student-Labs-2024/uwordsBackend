import pytest

from src.utils.password import hash_password, validate_password

class TestHashPassword:

    @pytest.mark.parametrize(
        "password",
        [
            "my_secure_password",
            "123456789",
            "gf98degdfsg1",
        ],
    )
    def test_hash_password(self, password):
        hashed_password = hash_password(password)
        assert hashed_password != password.encode()
        assert validate_password(password=password, hashed_password=hashed_password)

    @pytest.mark.parametrize(
        "password,expected",
        [
            ("securepassword", True),
            ("anotherpassword", False),
            ("wrongpassword", False),
            ("12345678", False),
            ("87654321", False),
        ],
    )
    def test_validate_password(self, password, expected):
        hashed_password = hash_password("securepassword")
        assert validate_password(password, hashed_password) == expected

