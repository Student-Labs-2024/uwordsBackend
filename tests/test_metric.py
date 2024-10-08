import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from src.config.instance import METRIC_TOKEN
from src.utils.metric import get_user_data, send_user_data


class TestMetric:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, expected_result", [(200, None), (500, None)])
    @patch("aiohttp.ClientSession.post")
    async def test_send_user_data(mock_post, status_code, expected_result):
        mock_response = AsyncMock()
        mock_response.status = status_code
        mock_post.return_value.__aenter__.return_value = mock_response

        data = {"key": "value"}
        server_url = "http://example.com"
        headers = {"Authorization": f"Bearer {METRIC_TOKEN}"}

        result = await send_user_data(data, server_url)

        mock_post.assert_called_once_with(url=server_url, headers=headers, json=data)
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_send_user_data_exception(mock_post):
        mock_post.side_effect = aiohttp.ClientError("Test exception")

        data = {"key": "value"}
        server_url = "http://example.com"
        headers = {"Authorization": f"Bearer {METRIC_TOKEN}"}

        result = await send_user_data(data, server_url)

        mock_post.assert_called_once_with(url=server_url, headers=headers, json=data)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status_code, expected_result", [(200, {"key": "value"}), (500, None)]
    )
    @patch("aiohttp.ClientSession.get")
    async def test_get_user_data(mock_get, status_code, expected_result):
        mock_response = AsyncMock()
        mock_response.status = status_code
        mock_response.json = AsyncMock(return_value=expected_result)
        mock_get.return_value.__aenter__.return_value = mock_response

        uwords_uid = "123"
        server_url = "http://example.com"
        headers = {"Authorization": f"Bearer {METRIC_TOKEN}"}

        result = await get_user_data(uwords_uid=uwords_uid, server_url=server_url)

        mock_get.assert_called_once_with(
            url=f"{server_url}?uwords_uid={uwords_uid}&is_union=True&metric_range=alltime",
            headers=headers
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_user_data_exception(mock_get):
        mock_get.side_effect = aiohttp.ClientError("Test exception")

        uwords_uid = "123"
        server_url = "http://example.com"
        headers = {"Authorization": f"Bearer {METRIC_TOKEN}"}

        result = await get_user_data(uwords_uid=uwords_uid, server_url=server_url)

        mock_get.assert_called_once_with(
            url=f"{server_url}?uwords_uid={uwords_uid}&is_union=True&metric_range=alltime",
            headers=headers
        )
        assert result is None
