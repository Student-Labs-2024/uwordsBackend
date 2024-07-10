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
CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL")

# MINIO
MINIO_ENDPOINT: str = os.environ.get("MINIO_ENDPOINT")
MINIO_ROOT_USER: str = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD: str = os.environ.get("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_VOICEOVER: str = os.environ.get("MINIO_BUCKET_VOICEOVER")
MINIO_BUCKET_PICTURE: str = os.environ.get("MINIO_BUCKET_PICTURE")

# SYSTEM
MINIO_HOST: str = os.environ.get("MINIO_HOST")
UPLOAD_DIR: Path = BASE_DIR / 'audio_transfer'
FASTAPI_SECRET: str = os.environ.get("FASTAPI_SECRET")


# TOKEN SETTINGS
PRIVATE_KEY: Path = BASE_DIR / "src" / "config" / "certs" / "key"
PUBLIC_KEY: Path = BASE_DIR / "src" / "config" / "certs" / "key.pub"

JWT_ALGORITHM: str = "RS256"

ACCESS_TOKEN_LIFETIME: int = 60 # minutes
REFRESH_TOKEN_LIFETIME: int = 30 # days

# SENTRY
SENTRY_URL: str = os.environ.get("SENTRY_URL")