import pytest
import requests
from unittest.mock import patch, MagicMock
from src.utils.metric import get_user_data, send_user_data

class TestMetric:
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, expected_result", [(200, None), (500, None)])
    @patch("requests.post")
    async def test_send_user_data(mock_post, status_code, expected_result):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_post.return_value = mock_response

        data = {"key": "value"}
        server_url = "http://example.com"

        result = await send_user_data(data, server_url)

        mock_post.assert_called_once_with(server_url, json=data)
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @patch("requests.post")
    async def test_send_user_data_exception(mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Test exception")

        data = {"key": "value"}
        server_url = "http://example.com"

        result = await send_user_data(data, server_url)

        mock_post.assert_called_once_with(server_url, json=data)
        assert result is None

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, expected_result", [(200, {"key": "value"}), (500, None)])
    @patch("requests.get")
    async def test_get_user_data(mock_get, status_code, expected_result):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        user_id = 123
        server_url = "http://example.com"

        result = await get_user_data(user_id, server_url)

        mock_get.assert_called_once_with(
            f"{server_url}?user_id={user_id}&is_union=True&metric_range=alltime"
        )
        assert result == expected_result

    @staticmethod
    @pytest.mark.asyncio
    @patch("requests.get")
    async def test_get_user_data_exception(mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test exception")

        user_id = 123
        server_url = "http://example.com"

        result = await get_user_data(user_id, server_url)

        mock_get.assert_called_once_with(
            f"{server_url}?user_id={user_id}&is_union=True&metric_range=alltime"
        )
        assert result is None

