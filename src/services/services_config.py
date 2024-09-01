import nltk
import torch
import pymorphy3
from minio import Minio
from nltk.corpus import stopwords
from check_swear import SwearingCheck
from better_profanity import profanity
from speech_recognition import Recognizer
from google.cloud.vision import ImageAnnotatorClient
from transformers import MarianMTModel, MarianTokenizer, AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from src.utils.logger import services_config_logger

from src.config.instance import (
    MINIO_ENDPOINT,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
    SPEECH_RECOGNITION,
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

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

services_config_logger.info(f"device: {device}, torch_dtype: {torch_dtype}")

# Загрузка моделей перевода (русский -> английский)
tokenizer_ru_en = MarianTokenizer.from_pretrained(TRANSLATION_RU_EN)
model_ru_en = MarianMTModel.from_pretrained(TRANSLATION_RU_EN).to(device)

# Загрузка моделей перевода (английский -> русский)
tokenizer_en_ru = MarianTokenizer.from_pretrained(TRANSLATION_EN_RU)
model_en_ru = MarianMTModel.from_pretrained(TRANSLATION_EN_RU).to(device)

# Загрузка модели распознавания речи
speech_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    SPEECH_RECOGNITION, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
speech_model.to(device)

speech_processor = AutoProcessor.from_pretrained(SPEECH_RECOGNITION)

speech_pipe = pipeline(
    "automatic-speech-recognition",
    model=speech_model,
    tokenizer=speech_processor.tokenizer,
    feature_extractor=speech_processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)
