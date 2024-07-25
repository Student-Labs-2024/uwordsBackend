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
MINIO_POLICY_JSON: Path = (
    BASE_DIR / "src" / "config" / "json_configs" / "minio_policy.json"
)

# SYSTEM
MINIO_HOST: str = os.environ.get("MINIO_HOST")
UPLOAD_DIR: Path = BASE_DIR / "audio_transfer"
FASTAPI_SECRET: str = os.environ.get("FASTAPI_SECRET")
ALLOWED_AUDIO_MIME_TYPES: set = {
    "audio/ogg",
    "audio/mpeg",
    "audio/wav",
    "audio/webm",
    "audio/mp3",
    "audio/x-m4a",
    "audio/x-wav",
}
ALLOWED_YOUTUBE_LINK_PATTERNS: set = {
    r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/)([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
    r"^(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
    r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
}
STUDY_DELAY: int = 86400  # seconds
STUDY_MAX_PROGRESS: int = 3
STUDY_WORDS_AMOUNT: int = 4
IMAGE_SAFETY_INDEX: int = 3
IMAGE_SAFETY_SCALE: list = [
    "UNKNOWN",
    "VERY_UNLIKELY",
    "UNLIKELY",
    "POSSIBLE",
    "LIKELY",
    "VERY_LIKELY",
]

# TOKEN SETTINGS
JWT_ALGORITHM: str = "HS256"

ACCESS_TOKEN_LIFETIME: int = 60  # minutes
REFRESH_TOKEN_LIFETIME: int = 30  # days

# SENTRY
SENTRY_URL: str = os.environ.get("SENTRY_URL")

# PIXABAY
PIX_TOKEN: str = os.environ.get("PIX_TOKEN")

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

# GOOGLE CLOUD
GOOGLE_APPLICATION_CREDENTIALS: Path = (
    BASE_DIR / "src" / "config" / "json_configs" / "google_credentials.json"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS.__str__()
