import nltk
import pymorphy3
from minio import Minio
from nltk.corpus import stopwords
from speech_recognition import Recognizer

from src.config.instance import MINIO_ENDPOINT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD


sr = Recognizer()
ma = pymorphy3.analyzer.MorphAnalyzer()

mc = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

nltk.download("stopwords")

STOPWORDS_EN = list(stopwords.words("english"))
STOPWORDS_RU = list(stopwords.words("russian"))
STOPWORDS = STOPWORDS_EN + STOPWORDS_RU
