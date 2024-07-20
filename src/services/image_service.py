import json
import logging
import requests
from typing import Union

from src.config.instance import PIX_TOKEN


logger = logging.getLogger("[SERVICES IMAGE]")
logging.basicConfig(level=logging.INFO)


class ImageDownloader:
    @staticmethod
    async def get_image_data(word: str) -> Union[bytes, None]:
        try:
            response = requests.get(
                url="https://pixabay.com/api/",
                params={
                    "key": PIX_TOKEN,
                    "q": "+".join(word.split()),
                    "lang": "en",
                    "per_page": 3,
                },
            )

            data = json.loads(response.text)
            image = data.get("hits", None)[0]

            image_data = requests.get(image.get("largeImageURL"))

            return image_data.content

        except Exception as e:
            logger.info(f"[DOWNLOAD] Error: {e}")
            return None
