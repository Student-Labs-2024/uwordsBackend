import os
from pathlib import Path
from typing import List
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
MINIO_BUCKET_PICTURE_ADULT: str = os.environ.get("MINIO_BUCKET_PICTURE_ADULT")
MINIO_BUCKET_PICTURE_MEDICAL: str = os.environ.get("MINIO_BUCKET_PICTURE_MEDICAL")
MINIO_BUCKET_PICTURE_VIOLENCE: str = os.environ.get("MINIO_BUCKET_PICTURE_VIOLENCE")
MINIO_BUCKET_PICTURE_RACY: str = os.environ.get("MINIO_BUCKET_PICTURE_RACY")
MINIO_BUCKET_SUBTOPIC_ICONS: str = os.environ.get("MINIO_BUCKET_SUBTOPIC_ICONS")
MINIO_BUCKET_ACHIEVEMENT_ICONS: str = os.environ.get("MINIO_BUCKET_ACHIEVEMENT_ICONS")
MINIO_POLICY_JSON: Path = (
    BASE_DIR / "src" / "config" / "json_configs" / "minio_policy.json"
)
MINIO_BUCKETS: List[str] = [
    MINIO_BUCKET_VOICEOVER,
    MINIO_BUCKET_PICTURE,
    MINIO_BUCKET_PICTURE_ADULT,
    MINIO_BUCKET_PICTURE_MEDICAL,
    MINIO_BUCKET_PICTURE_VIOLENCE,
    MINIO_BUCKET_PICTURE_RACY,
    MINIO_BUCKET_SUBTOPIC_ICONS,
]

# SYSTEM
MINIO_HOST: str = os.environ.get("MINIO_HOST")
UPLOAD_DIR: Path = BASE_DIR / "audio_transfer"
SERVICE_SECRET: str = os.environ.get("SERVICE_SECRET")
ADMIN_SECRET: str = os.environ.get("ADMIN_SECRET")
ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS")
ALLOWED_ORIGINS_LIST = ALLOWED_ORIGINS.split(",")

ALLOWED_AUDIO_MIME_TYPES: set = {
    "audio/ogg",
    "audio/mpeg",
    "audio/wav",
    "audio/webm",
    "audio/mp3",
    "audio/x-m4a",
    "audio/x-wav",
}
ALLOWED_ICON_MIME_TYPES: set = {"image/svg+xml", "image/svg+xml-compressed"}
ALLOWED_YOUTUBE_LINK_PATTERNS: set = {
    r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/)([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
    r"^(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
    r"^(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})(?:[&?].*)?$",
}

STUDY_DELAY: int = 86400  # seconds
STUDY_MAX_PROGRESS: int = 4
STUDY_WORDS_AMOUNT: int = 4
STUDY_RANDOM_PIC: int = 12

IMAGE_SAFETY_INDEX: int = 3
IMAGE_SAFETY_SCALE: List[str] = [
    "UNKNOWN",
    "VERY_UNLIKELY",
    "UNLIKELY",
    "POSSIBLE",
    "LIKELY",
    "VERY_LIKELY",
]

DEFAULT_SUBTOPIC: str = "Unsorted"
DEFAULT_SUBTOPIC_ICON: str = (
    f"{MINIO_HOST}/{MINIO_BUCKET_SUBTOPIC_ICONS}/Default Subtopic.svg"
)

ALLOWED_AUDIO_SECONDS: int = 1800
ALLOWED_VIDEO_SECONDS: int = 900
DEFAULT_ENERGY: int = 100

# TOKEN SETTINGS
JWT_ALGORITHM: str = "HS256"
JWT_SECRET: str = os.environ.get("JWT_SECRET")
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
EMAIL_CODE_LEN: int = 4
TELEGRAM_CODE_LEN: int = 12

# VK
IOS_SERVICE_TOKEN = os.environ.get("IOS_SERVICE_TOKEN")
ANDROID_SERVICE_TOKEN = os.environ.get("ANDROID_SERVICE_TOKEN")
VK_API_VERSION = "5.199"

# GOOGLE CLOUD
GOOGLE_APPLICATION_CREDENTIALS: Path = (
    BASE_DIR / "src" / "config" / "json_configs" / "google_credentials.json"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS.__str__()

# METRIC
METRIC_URL: str = os.environ.get("METRIC_URL")
METRIC_TOKEN: str = os.environ.get("METRIC_TOKEN")

# DOWNLOADER
DOWNLOADER_URL: str = os.environ.get("DOWNLOADER_URL")
DOWNLOADER_TOKEN: str = os.environ.get("DOWNLOADER_TOKEN")

# PAYMENT
PAYMENT_TOKEN: str = os.environ.get("PAYMENT_TOKEN")
WALLET_ID: str = os.environ.get("WALLET_ID")

# HUGGINGFACE
HUGGING_FACE_URL: str = (
    "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
)
HUGGING_FACE_TOKEN: str = os.environ.get("HUGGING_FACE_TOKEN")
SUBTOPIC_COUNT_WORDS = 8

ACHIEVEMENT_WORDS: str = "added_words"
ACHIEVEMENT_LEARNED: str = "learned_words"
ACHIEVEMENT_AUDIO: str = "speech_seconds"
ACHIEVEMENT_VIDEO: str = "video_seconds"
