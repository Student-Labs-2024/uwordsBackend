import logging
import aiohttp
from io import BytesIO
from typing import Union

from src.config.instance import (
    MINIO_BUCKET_PICTURE,
    MINIO_BUCKET_PICTURE_ADULT,
    MINIO_BUCKET_PICTURE_MEDICAL,
    MINIO_BUCKET_PICTURE_RACY,
    MINIO_BUCKET_PICTURE_VIOLENCE,
    MINIO_HOST,
    DOWNLOADER_URL,
    DOWNLOADER_TOKEN,
)

from src.schemes.enums.enums import ImageAnnotations
from src.services.censore_service import ImageSafetyVision
from src.services.minio_uploader import MinioUploader
from src.utils.logger import image_service_logger
from src.utils.helpers import generate_object_name


class ImageDownloader:
    @staticmethod
    async def get_image_data(word: str) -> Union[bytes, None]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=f"{DOWNLOADER_URL}/api/v1/pixabay/download",
                    params={"word": word},
                    headers={"Authorization": f"Bearer {DOWNLOADER_TOKEN}"},
                ) as response:
                    if response.status != 200:
                        return None
                    return await response.read()

        except Exception as e:
            image_service_logger.error(f"[DOWNLOAD] Error: {e}")
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

            object_name = await generate_object_name(word)

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
                annotation_type = annotation["type"]
                if annotation_type == ImageAnnotations.adult.value:
                    bucket_name = MINIO_BUCKET_PICTURE_ADULT
                elif annotation_type == ImageAnnotations.medical.value:
                    bucket_name = MINIO_BUCKET_PICTURE_MEDICAL
                elif annotation_type == ImageAnnotations.violence.value:
                    bucket_name = MINIO_BUCKET_PICTURE_VIOLENCE
                elif annotation_type == ImageAnnotations.racy.value:
                    bucket_name = MINIO_BUCKET_PICTURE_RACY

                annotation_value = annotation["value"]

                object_name = await generate_object_name(word, annotation_value)

                await MinioUploader.upload_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    data=bytes_file,
                    lenght=bytes_file.getbuffer().nbytes,
                    type="image/jpeg",
                )

                link = f"{MINIO_HOST}/{bucket_name}/{object_name}"

                image_service_logger.info(f"[IMAGE SAFETY] Image not safety: {link}")
                return None

        except BaseException as e:
            image_service_logger.error(f"[DOWNLOAD PICTURE] Error: {e}")
            return None
