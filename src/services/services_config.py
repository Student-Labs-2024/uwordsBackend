import nltk
import pymorphy3
from minio import Minio
from nltk.corpus import stopwords
from check_swear import SwearingCheck
from better_profanity import profanity
from speech_recognition import Recognizer
from google.cloud.vision import ImageAnnotatorClient
from transformers import MarianMTModel, MarianTokenizer

from src.config.instance import (
    MINIO_ENDPOINT,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
    TRANSLATION_EN_RU,
    TRANSLATION_RU_EN,
)


sr: Recognizer = Recognizer()
ma = pymorphy3.analyzer.MorphAnalyzer()

mc = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

nltk.download("stopwords")

profanity.load_censor_words()

swear_check = SwearingCheck()

STOPWORDS_EN = list(stopwords.words("english"))
STOPWORDS_RU = list(stopwords.words("russian"))
STOPWORDS = STOPWORDS_EN + STOPWORDS_RU

google_vision = ImageAnnotatorClient()

tokenizer_ru_en = MarianTokenizer.from_pretrained(TRANSLATION_RU_EN)
model_ru_en = MarianMTModel.from_pretrained(TRANSLATION_RU_EN)

tokenizer_en_ru = MarianTokenizer.from_pretrained(TRANSLATION_EN_RU)
model_en_ru = MarianMTModel.from_pretrained(TRANSLATION_EN_RU)
