import json
import logging
import requests
from io import BytesIO
from typing import Union

from src.config.instance import (
    MINIO_BUCKET_PICTURE,
    MINIO_BUCKET_PICTURE_ADULT,
    MINIO_BUCKET_PICTURE_MEDICAL,
    MINIO_BUCKET_PICTURE_RACY,
    MINIO_BUCKET_PICTURE_VIOLENCE,
    MINIO_HOST,
    PIX_TOKEN,
)

from src.schemes.enums import ImageAnnotations
from src.services.censore_service import ImageSafetyVision
from src.services.minio_uploader import MinioUploader


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

    @staticmethod
    async def download_picture(
        word: str,
    ) -> Union[str, None]:
        try:
            image_data = await ImageDownloader.get_image_data(word=word)

            bytes_file = BytesIO(image_data)
            bytes_file.seek(0)

            is_safe, annotations = await ImageSafetyVision.check_image_safety(
                image_content=image_data
            )

            object_name = f'{"_".join(word.lower().split())}.jpg'

            if is_safe:

                await MinioUploader.upload_object(
                    bucket_name=MINIO_BUCKET_PICTURE,
                    object_name=object_name,
                    data=bytes_file,
                    lenght=bytes_file.getbuffer().nbytes,
                    type="image/jpeg",
                )

                return f"{MINIO_HOST}/{MINIO_BUCKET_PICTURE}/{object_name}"

            for annotation in annotations:
                match annotation["type"]:
                    case ImageAnnotations.adult.value:
                        bucket_name = MINIO_BUCKET_PICTURE_ADULT
                    case ImageAnnotations.medical.value:
                        bucket_name = MINIO_BUCKET_PICTURE_MEDICAL
                    case ImageAnnotations.violence.value:
                        bucket_name = MINIO_BUCKET_PICTURE_VIOLENCE
                    case ImageAnnotations.racy.value:
                        bucket_name = MINIO_BUCKET_PICTURE_RACY

                annotation_value = annotation["value"]

                object_name = f'{annotation_value}-{"_".join(word.lower().split())}.jpg'

                await MinioUploader.upload_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    data=bytes_file,
                    lenght=bytes_file.getbuffer().nbytes,
                    type="image/jpeg",
                )

                link = f"{MINIO_HOST}/{bucket_name}/{object_name}"

                logger.info(f"[IMAGE SAFETY] Image not safety: {link}")
                return None

        except BaseException as e:
            logger.info(f"[DOWNLOAD PICTURE] Error: {e}")
            return None
