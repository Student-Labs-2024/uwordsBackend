import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from unittest.mock import AsyncMock, MagicMock, patch

from src.config.instance import ANDROID_SERVICE_TOKEN, IOS_SERVICE_TOKEN, VK_API_VERSION
from src.database.models import User
from src.schemes.enums.enums import Platform
from src.services.user_service import UserService

from src.utils.auth import (
    get_active_current_user,
    get_admin_user,
    get_current_token_payload,
    get_current_user,
    get_current_user_by_refresh,
    get_user_by_token,
    validate_token,
    validate_vk_token,
)


@pytest.fixture(autouse=True)
def reset_mocks(mock_decode_jwt, mock_user_service):
    mock_decode_jwt.reset_mock()
    mock_user_service.reset_mock()


@pytest.fixture
def mock_decode_jwt():
    with patch("src.utils.tokens.decode_jwt", new_callable=MagicMock) as mock:
        yield mock


@pytest.fixture
def mock_user_service():
    mock = AsyncMock(spec=UserService)
    with patch("src.services.user_service.UserService", new=mock):
        yield mock


class TestAuth:
    @pytest.mark.parametrize(
        "token,payload",
        [
            ("valid_token_1", {"user_id": 1, "exp": 1234567890}),
            ("valid_token_2", {"user_id": 2, "exp": 1234567891}),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_current_token_payload_valid_token(
        self, mock_decode_jwt, token, payload
    ):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        mock_decode_jwt.return_value = payload

        result = await get_current_token_payload(credentials)

        assert result == payload
        mock_decode_jwt.assert_called_once_with(token=token)

    @pytest.mark.parametrize(
        "token,exception",
        [
            ("invalid_token_1", InvalidTokenError("Invalid token")),
            ("invalid_token_2", InvalidTokenError("Another invalid token")),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_current_token_payload_invalid_token(
        self, mock_decode_jwt, token, exception
    ):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        mock_decode_jwt.side_effect = exception

        with pytest.raises(HTTPException) as exc_info:
            await get_current_token_payload(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == {"msg": "Invalid token"}
        mock_decode_jwt.assert_called_once_with(token=token)

    @pytest.mark.parametrize(
        "payload,token_type",
        [
            ({"type": "access"}, "access"),
            ({"type": "refresh"}, "refresh"),
        ],
    )
    @pytest.mark.asyncio
    async def test_validate_token_valid(self, payload, token_type):
        result = await validate_token(payload, token_type)

        assert result is True

    @pytest.mark.parametrize(
        "payload,token_type,expected_detail",
        [
            (
                {"type": "access"},
                "refresh",
                {"msg": "Invalid token type: 'access' | expected: 'refresh'"},
            ),
            (
                {"type": "refresh"},
                "access",
                {"msg": "Invalid token type: 'refresh' | expected: 'access'"},
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, payload, token_type, expected_detail):
        with pytest.raises(HTTPException) as exc_info:
            await validate_token(payload, token_type)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == expected_detail

    @pytest.mark.parametrize(
        "payload,user_id,expected_user",
        [
            ({"user_id": 1}, 1, User(id=1, username="Test User")),
            ({"user_id": 2}, 2, User(id=2, username="Another User")),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_user_by_token_valid(
        self, mock_user_service, payload, user_id, expected_user
    ):
        mock_user_service.get_user_by_id.return_value = expected_user

        result = await get_user_by_token(payload, user_service=mock_user_service)

        assert result == expected_user
        mock_user_service.get_user_by_id.assert_called_once_with(user_id=user_id)

    @pytest.mark.parametrize(
        "payload,expected_detail",
        [
            ({"user_id": None}, {"msg": "User with ID None not found"}),
            ({"user_id": 0}, {"msg": "User with ID 0 not found"}),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_user_by_token_invalid(
        self, mock_user_service, payload, expected_detail
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_token(payload, user_service=mock_user_service)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == expected_detail

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, validate_token_exception, get_user_by_token_result, expected_exception",
        [
            ({"user_id": 1}, None, User(id=1, is_active=True), None),
            (
                {"user_id": 1},
                HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                ),
                None,
                HTTPException,
            ),
        ],
    )
    @patch("src.utils.auth.get_current_token_payload", new_callable=AsyncMock)
    @patch("src.utils.auth.validate_token", new_callable=AsyncMock)
    @patch("src.utils.auth.get_user_by_token", new_callable=AsyncMock)
    async def test_get_current_user(
        self,
        get_user_by_token_mock,
        validate_token_mock,
        get_current_token_payload_mock,
        payload,
        validate_token_exception,
        get_user_by_token_result,
        expected_exception,
    ):
        get_current_token_payload_mock.return_value = payload
        get_user_by_token_mock.return_value = get_user_by_token_result

        if validate_token_exception:
            validate_token_mock.side_effect = validate_token_exception

        if expected_exception:
            with pytest.raises(expected_exception):
                await get_current_user(payload=payload)
        else:
            result = await get_current_user(payload=payload)
            assert result == get_user_by_token_result

        validate_token_mock.assert_called_once_with(
            payload=payload, token_type="access"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload, validate_token_exception, get_user_by_token_result, expected_exception",
        [
            ({"user_id": 1, "type": "refresh"}, None, User(id=1, is_active=True), None),
            (
                {"user_id": 1, "type": "invalid"},
                HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "msg": "Invalid token type: 'invalid' | expected: 'refresh'"
                    },
                ),
                None,
                HTTPException,
            ),
        ],
    )
    @patch("src.utils.auth.get_current_token_payload", new_callable=AsyncMock)
    @patch("src.utils.auth.validate_token", new_callable=AsyncMock)
    @patch("src.utils.auth.get_user_by_token", new_callable=AsyncMock)
    async def test_get_current_user_by_refresh(
        self,
        get_user_by_token_mock,
        validate_token_mock,
        get_current_token_payload_mock,
        payload,
        validate_token_exception,
        get_user_by_token_result,
        expected_exception,
    ):
        get_current_token_payload_mock.return_value = payload
        get_user_by_token_mock.return_value = get_user_by_token_result

        if validate_token_exception:
            validate_token_mock.side_effect = validate_token_exception

        if expected_exception:
            with pytest.raises(expected_exception):
                await get_current_user_by_refresh(payload=payload)
        else:
            result = await get_current_user_by_refresh(payload=payload)
            assert result == get_user_by_token_result

        validate_token_mock.assert_called_once_with(
            payload=payload, token_type="refresh"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user, expected_exception, expected_detail",
        [
            (User(id=1, is_active=True), None, None),
            (User(id=1, is_active=False), HTTPException, {"msg": "User 1 banned"}),
            (None, HTTPException, {"msg": "User do not exist"}),
        ],
    )
    async def test_get_active_current_user(
        self, user, expected_exception, expected_detail
    ):
        get_current_user = AsyncMock(return_value=user)

        if expected_exception:
            with pytest.raises(expected_exception) as exc_info:
                await get_active_current_user(user=user)
            assert (
                exc_info.value.status_code == status.HTTP_403_FORBIDDEN
                if user
                else status.HTTP_404_NOT_FOUND
            )
            assert exc_info.value.detail == expected_detail
        else:
            result = await get_active_current_user(user=user)
            assert result == user

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_superuser, email, expected_exception",
        [
            (True, "admin@example.com", None),
            (False, "user@example.com", HTTPException),
        ],
    )
    async def test_get_admin_user(self, is_superuser, email, expected_exception):
        user = User(is_superuser=is_superuser, email=email)

        get_active_current_user = AsyncMock(return_value=user)

        if expected_exception:
            with pytest.raises(expected_exception) as exc_info:
                await get_admin_user(user=user)
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == {"msg": f"User {email} not a superuser"}
        else:
            result = await get_admin_user(user=user)
            assert result == user

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "platform, token, response_text, expected_response, expected_exception, expected_detail",
        [
            (
                Platform.ios.value,
                "valid_token",
                '{"response": true}',
                {"response": True},
                None,
                None,
            ),
            (
                Platform.android.value,
                "valid_token",
                '{"response": true}',
                {"response": True},
                None,
                None,
            ),
            (
                Platform.ios.value,
                "invalid_token",
                '{"error": "Invalid token"}',
                None,
                HTTPException,
                "Invalid token",
            ),
            (
                "invalid_platform",
                "valid_token",
                "",
                None,
                HTTPException,
                "Invalid platform",
            ),
        ],
    )
    @patch("aiohttp.ClientSession.get")
    async def test_validate_vk_token(
        self,
        mock_get,
        platform,
        token,
        response_text,
        expected_response,
        expected_exception,
        expected_detail,
    ):
        credentials = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")
        mock_response = AsyncMock()
        mock_response.text.return_value = response_text
        mock_get.return_value.__aenter__.return_value = mock_response

        if expected_exception:
            with pytest.raises(expected_exception) as exc_info:
                await validate_vk_token(platform=platform, credentials=credentials)
            assert exc_info.value.detail == expected_detail
        else:
            result = await validate_vk_token(platform=platform, credentials=credentials)
            assert result.get("response") == expected_response.get("response")

        if platform in [Platform.ios.value, Platform.android.value]:
            service_token = (
                IOS_SERVICE_TOKEN
                if platform == Platform.ios.value
                else ANDROID_SERVICE_TOKEN
            )
            mock_get.assert_called_once_with(
                f"https://api.vk.com/method/secure.checkToken?v={VK_API_VERSION}&token={token}",
                headers={"Authorization": f"Bearer {service_token}"},
            )
        else:
            mock_get.assert_not_called()
