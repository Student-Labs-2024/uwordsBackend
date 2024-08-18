import logging
from typing import BinaryIO

from src.services.services_config import mc

from src.config.instance import MINIO_BUCKETS, MINIO_POLICY_JSON


logger = logging.getLogger("[SERVICES MINIO]")
logging.basicConfig(level=logging.INFO)


class MinioUploader:
    @staticmethod
    async def check_buckets() -> None:
        for bucket_name in MINIO_BUCKETS:
            found_bucket = mc.bucket_exists(bucket_name)
            if not found_bucket:
                await MinioUploader.create_bucket(found_bucket)

    @staticmethod
    async def create_bucket(bucket_name: str) -> None:
        try:

            with open(MINIO_POLICY_JSON, "r") as json_policy:
                policy = json_policy.read()
                json_policy.close()

            policy = policy.replace("{{bucket_name}}", bucket_name)

            mc.make_bucket(bucket_name)
            mc.set_bucket_policy(bucket_name, policy)

            logger.info(f"[BUCKET] Created {bucket_name}")

        except Exception as e:
            logger.info(f"[BUCKET] Error: {e}")

    @staticmethod
    async def upload_object(
        bucket_name: str, object_name: str, data: BinaryIO, lenght: int, type: str
    ) -> None:
        try:
            mc.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=lenght,
                part_size=10 * 1024 * 1024,
                content_type=type,
            )

            logger.info(f"[UPLOAD] File: {object_name}")

        except Exception as e:
            logger.info(f"[UPLOAD] Error: {e}")
