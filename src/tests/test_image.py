import pytest
import requests_mock

from src.services.image_service import ImageDownloader


class TestGetImage:
    @staticmethod
    def test_get_image_data_success():
        word = "test"

        pixabay_response = {
            "hits": [{"largeImageURL": "https://example.com/test_image.jpg"}]
        }

        image_data = b"fake_image_data"

        with requests_mock.Mocker() as m:
            m.get("https://pixabay.com/api/", json=pixabay_response)

            m.get("https://example.com/test_image.jpg", content=image_data)

            result = ImageDownloader.get_image_data(word)

            assert result == image_data

    @staticmethod
    def test_get_image_data_failure():
        word = "test"

        with requests_mock.Mocker() as m:

            m.get("https://pixabay.com/api/", status_code=404)

            result = ImageDownloader.get_image_data(word)

            assert result is None


def test_sum():
    x = 1
    y = 2
    assert x + y == 3
