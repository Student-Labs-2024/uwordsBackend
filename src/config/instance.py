import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent

# PostgreSQL
POSTGRES_DB: str = os.environ.get("POSTGRES_DB")
POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT")
POSTGRES_USER: str = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")

# REDIS
REDIS_URL: str = os.environ.get("REDIS_URL")
REDIS_HOST: str = os.environ.get("REDIS_HOST")
REDIS_PORT: str = os.environ.get("REDIS_PORT")
REDIS_PASS: str = os.environ.get("REDIS_PASS")

# MINIO
MINIO_ENDPOINT: str = os.environ.get("MINIO_ENDPOINT")
MINIO_ROOT_USER: str = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD: str = os.environ.get("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_VOICEOVER: str = os.environ.get("MINIO_BUCKET_VOICEOVER")
MINIO_BUCKET_PICTURE: str = os.environ.get("MINIO_BUCKET_PICTURE")

# SYSTEM
MINIO_HOST: str = os.environ.get("MINIO_HOST")
UPLOAD_DIR: Path = BASE_DIR / "audio_transfer"
FASTAPI_SECRET: str = os.environ.get("FASTAPI_SECRET")

# TOKEN SETTINGS
JWT_ALGORITHM: str = "HS256"

ACCESS_TOKEN_LIFETIME: int = 60  # minutes
REFRESH_TOKEN_LIFETIME: int = 30  # days

# SENTRY
SENTRY_URL: str = os.environ.get("SENTRY_URL")

# EMAIl
EMAIL_CODE_EXP: str = os.environ.get("EMAIL_CODE_EXP")
EMAIL_CODE_ATTEMPTS: str = os.environ.get("EMAIL_CODE_ATTEMPTS")
EMAIL_PORT: str = os.environ.get("EMAIL_PORT")
SMTP_SERVER: str = os.environ.get("SMTP_SERVER")
SENDER_EMAIL: str = os.environ.get("SENDER_EMAIL")
EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD")
EMAIL_CODE_LEN: str = os.environ.get("EMAIL_CODE_LEN")

# VK
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN")
