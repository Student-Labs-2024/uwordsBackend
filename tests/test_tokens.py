import jwt
import pytest

from src.database.models import User
from src.utils.tokens import (
    encode_jwt,
    decode_jwt,
    create_jwt,
    create_access_token,
    create_refresh_token,
)


class TestJWT:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload_data, payload_data_invalid, token_invalid",
        [
            ({"test": "test", "type": "access"}, {"test": "test"}, "gdfg"),
            ({"test": "test2", "type": "refresh"}, {"test": "test1"}, "323123"),
        ],
    )
    async def test_decode_and_encode_jwt(
        payload_data, payload_data_invalid, token_invalid
    ):
        token = encode_jwt(payload=payload_data)
        assert decode_jwt(token)
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            assert decode_jwt(token_invalid)
        with pytest.raises(UnboundLocalError):
            token = encode_jwt(payload=payload_data_invalid)
            assert decode_jwt(token)

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "token_type, payload, token_type_invalid",
        [
            ("access", {"test": "test"}, "accfdgdfgess"),
            ("refresh", {"test": "test2"}, "3213458"),
        ],
    )
    async def test_create_jwt(token_type, payload, token_type_invalid):
        token = create_jwt(token_type, payload)
        assert decode_jwt(token)
        with pytest.raises(UnboundLocalError):
            token = create_jwt(token_type_invalid, payload)
            assert decode_jwt(token)

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_data, token_type",
        [
            ({"id": 1, "email": "jojo@gmail.com"}, "access"),
            ({"id": 2, "email": "jane@gmail.com"}, "refresh"),
        ],
    )
    async def test_create_refresh_and_access_tokens(user_data, token_type):
        user = User(**user_data)
        token = (
            create_access_token(user)
            if token_type == "access"
            else create_refresh_token(user)
        )
        assert decode_jwt(token)
        payload = decode_jwt(token)
        assert payload["type"] == token_type
