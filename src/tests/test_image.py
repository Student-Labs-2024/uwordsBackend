import pytest
import requests_mock

from src.services.image_service import ImageDownloader


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word,pixabay_response,image_data,expected_result",
    [
        (
            "test",
            {"hits": [{"largeImageURL": "https://example.com/test_image.jpg"}]},
            b"fake_image_data",
            b"fake_image_data",
        ),
        (
            "test2",
            {"hits": [{"largeImageURL": "https://example.com/test2_image.jpg"}]},
            b"fake_image_data2",
            b"fake_image_data2",
        ),
    ],
)
async def test_get_image_data_success(
    word, pixabay_response, image_data, expected_result
):
    with requests_mock.Mocker() as m:
        m.get("https://pixabay.com/api/", json=pixabay_response)

        m.get(pixabay_response["hits"][0]["largeImageURL"], content=image_data)

        result = await ImageDownloader.get_image_data(word)

        assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word,pixabay_response,expected_result",
    [
        ("test", {"hits": []}, None),
        (
            "test2",
            {"hits": [{"largeImageURL": "https://example.com/test2_image.jpg"}]},
            None,
        ),
    ],
)
async def test_get_image_data_failure(word, pixabay_response, expected_result):
    with requests_mock.Mocker() as m:
        m.get("https://pixabay.com/api/", json=pixabay_response)

        result = await ImageDownloader.get_image_data(word)

        assert result == expected_result
