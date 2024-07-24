import pytest

from src.utils.auth import hash_password, validate_password


@pytest.mark.parametrize(
    "password",
    [
        "my_secure_password",
        "123456789",
        "gf98degdfsg1",
    ],
)
def test_hash_password(password):

    hashed_password = hash_password(password)

    assert hashed_password != password.encode()

    assert validate_password(password=password, hashed_password=hashed_password)
