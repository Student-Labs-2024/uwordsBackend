import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

# PostgreSQL
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

# REDIS
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

# MINIO
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_VOICEOVER = os.environ.get("MINIO_BUCKET_VOICEOVER")
MINIO_BUCKET_PICTURE = os.environ.get("MINIO_BUCKET_PICTURE")

# SYSTEM
MINIO_HOST = os.environ.get("MINIO_HOST")
UPLOAD_DIR = Path() / 'audio_transfer'
FASTAPI_SECRET = os.environ.get("FASTAPI_SECRET")
