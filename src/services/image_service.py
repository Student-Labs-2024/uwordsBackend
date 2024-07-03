import json

import requests


class ImageDownloader:

    @staticmethod
    def get_image_data(word: str):
        try:
            response = requests.get(
                url='https://pixabay.com/api/',
                params={
                    "key": "44077916-f2200c27f389302121ab3a8e5",
                    "q": "+".join(word.split()),
                    "lang": "en",
                    "per_page": 3
                }
            )

            data = json.loads(response.text)
            image = data.get("hits", None)[0]

            image_data = requests.get(image.get("largeImageURL"))

            return image_data.content

        except:
            return None
