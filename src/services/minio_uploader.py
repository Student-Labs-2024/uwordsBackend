import json
import logging
from typing import BinaryIO

from src.services.services_config import mc

logger = logging.getLogger("[SERVICES AUDIO]")
logging.basicConfig(level=logging.INFO)


class MinioUploader:

    @staticmethod
    def create_bucket(bucket_name: str):

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}",
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                },
            ],
        }

        mc.make_bucket(bucket_name)
        mc.set_bucket_policy(bucket_name, json.dumps(policy))

        logger.info(f'[MINIO] Created bucket {bucket_name}')

    @staticmethod
    def upload_object(bucket_name: str, object_name: str, data: BinaryIO, lenght: int, type: str):
        try:
            mc.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=lenght,
                part_size=10 * 1024 * 1024,
                content_type=type
            )

            logger.info(f'[MINIO] Uploaded file {object_name}')

        except Exception as e:
            logger.info(f'[MINIO] Error uploading file {object_name}')
            logger.info(e)
