import pymorphy3
from minio import Minio
from speech_recognition import Recognizer

from src.config.instance import MINIO_ENDPOINT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD
from src.utils.stopwords import STOPWORDS_EN, STOPWORDS_RU

sr = Recognizer()
ma = pymorphy3.analyzer.MorphAnalyzer()

mc = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)
STOPWORDS = STOPWORDS_EN + STOPWORDS_RU
