import jwt
import pytest

from src.database.models import User
from src.utils.tokens import encode_jwt, decode_jwt, create_jwt, create_access_token, create_refresh_token


class TestJWT:
    @staticmethod
    @pytest.mark.asyncio
    async def test_decode_and_encode_jwt():
        payload = {"test": "test", "type": "access"}
        token = encode_jwt(payload=payload)
        assert decode_jwt(token)
        token = "gdfg"
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            assert decode_jwt(token)
        with pytest.raises(UnboundLocalError):
            payload = {"test": "test"}
            token = encode_jwt(payload=payload)
            assert decode_jwt(token)

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_jwt():
        token_type = "access"
        payload = {"test": "test"}
        token = create_jwt(token_type, payload)
        assert decode_jwt(token)
        with pytest.raises(UnboundLocalError):
            token_type = "accfdgdfgess"
            token = create_jwt(token_type, payload)
            assert decode_jwt(token)

    @staticmethod
    @pytest.mark.asyncio
    async def test_create_refresh_and_access_tokens():
        user = User()
        user.id = 1
        user.email = "jojo@gmail.com"
        token = create_access_token(user)
        assert decode_jwt(token)
        payload = decode_jwt(token)
        assert payload['type'] == 'access'
        token = create_refresh_token(user)
        assert decode_jwt(token)
        payload = decode_jwt(token)
        assert payload['type'] == 'refresh'
