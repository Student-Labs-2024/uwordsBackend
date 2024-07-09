import os
import uuid
import asyncio
import logging
import subprocess
from io import BytesIO

from gtts import gTTS
from pydub import AudioSegment
from pytube import YouTube
from speech_recognition import AudioFile

from src.config.instance import (
    MINIO_BUCKET_VOICEOVER,
    MINIO_HOST,
    UPLOAD_DIR,
    MINIO_BUCKET_PICTURE,
)
from src.schemes.schemas import ErrorCreate
from src.services.image_service import ImageDownloader
from src.services.minio_uploader import MinioUploader
from src.services.services_config import sr
from src.services.error_service import ErrorService

logger = logging.getLogger("[SERVICES AUDIO]")
logging.basicConfig(level=logging.INFO)


class AudioService:
    @staticmethod
    def convert_audio(
        path: str, title: str, error_service: ErrorService, user_id: str
    ) -> str | None:
        try:
            out_path = UPLOAD_DIR / title
            logger.info(f"OUT_PATH: {out_path}")
            cmd = f"ffmpeg -i {path} -ac 1 {out_path} -y"

            subprocess.call(cmd, shell=True)

            return str(out_path)

        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[CONVERT AUDIO] Ошибка конвертации аудио!",
                description=str(e),
            )
            asyncio.run(error_service.add_one(error=error))

            return None

    @staticmethod
    def cut_audio(path: str, error_service: ErrorService, user_id: str) -> list[str]:
        files = []

        try:
            index = 0
            duration = int(len(AudioSegment.from_file(file=path)) / 1000)

            while index * 30 < duration:
                filename, _ = os.path.splitext(path)

                logger.info(
                    f"[AUDIO] path: {path} new_path: {filename}_{index + 1}.wav"
                )

                if (index + 1) * 30 < duration:
                    cmd = f"ffmpeg -ss {index * 30} -i {path} -t 30 -ac 1 {filename}_{index + 1}.wav -y"
                else:
                    cmd = f"ffmpeg -ss {index * 30} -i {path} -ac 1 {filename}_{index + 1}.wav -y"

                subprocess.call(cmd, shell=True)

                files.append(f"{filename}_{index + 1}.wav")
                index += 1

            return files

        except Exception as e:
            logger.info(e)

            error = ErrorCreate(
                user_id=user_id,
                message="[UPLOAD AUDIO] Ошибка обработки видео!",
                description=str(e),
            )

            asyncio.run(error_service.add_one(error=error))

            return files

    @staticmethod
    def speech_to_text_ru(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="ru-RU")

                return text.lower()

        except Exception as e:
            logger.info(e)
            return " "

    @staticmethod
    def speech_to_text_en(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="en-US")

                return text.lower()

        except Exception as e:
            logger.info(e)
            return " "

    @staticmethod
    def upload_youtube_audio(link: str, error_service: ErrorService, user_id: str):
        try:
            video = YouTube(link)

            stream = video.streams.filter(only_audio=True).first()

            filename = f"audio_{uuid.uuid4()}.mp3"

            download_path = UPLOAD_DIR / filename

            stream.download(filename=download_path)

            return download_path, filename, video.title

        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[UPLOAD YOUTUBE AUDIO] Ошибка выгрузки аудио из ютуба!",
                description=str(e),
            )

            asyncio.run(error_service.add_one(error=error))

            return None

    @staticmethod
    def word_to_speech(word: str) -> str | None:
        try:
            tts = gTTS(text=word, lang="en", slow=False)

            bytes_file = BytesIO()
            tts.write_to_fp(bytes_file)
            bytes_file.seek(0)

            object_name = f'{"_".join(word.lower().split())}.mp3'

            MinioUploader.upload_object(
                bucket_name=MINIO_BUCKET_VOICEOVER,
                object_name=object_name,
                data=bytes_file,
                lenght=bytes_file.getbuffer().nbytes,
                type="audio/mpeg",
            )

            return f"{MINIO_HOST}/{MINIO_BUCKET_VOICEOVER}/{object_name}"

        except BaseException as e:
            logger.info(e)
            return None

    @staticmethod
    def download_picture(word: str) -> str | None:
        try:
            image_data = ImageDownloader.get_image_data(word=word)
            bytes_file = BytesIO(image_data)
            bytes_file.seek(0)

            object_name = f'{"_".join(word.lower().split())}.jpg'

            MinioUploader.upload_object(
                bucket_name=MINIO_BUCKET_PICTURE,
                object_name=object_name,
                data=bytes_file,
                lenght=bytes_file.getbuffer().nbytes,
                type="image/jpeg",
            )

            return f"{MINIO_HOST}/{MINIO_BUCKET_PICTURE}/{object_name}"

        except BaseException as e:
            logger.info(e)
            return None
