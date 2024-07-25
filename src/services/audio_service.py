import os
import uuid
import yt_dlp
import ffmpeg
import logging
from gtts import gTTS
from io import BytesIO
from pathlib import Path
from pydub import AudioSegment
from typing import Union, Tuple
from speech_recognition import AudioFile

from src.schemes.schemas import ErrorCreate
from src.schemes.enums import ImageAnnotations

from src.services.services_config import sr
from src.services.error_service import ErrorService
from src.services.minio_uploader import MinioUploader
from src.services.image_service import ImageDownloader
from src.services.censore_service import ImageSafetyVision

from src.config.instance import (
    MINIO_BUCKET_VOICEOVER,
    MINIO_HOST,
    UPLOAD_DIR,
    MINIO_BUCKET_PICTURE,
    MINIO_BUCKET_PICTURE_ADULT,
    MINIO_BUCKET_PICTURE_MEDICAL,
    MINIO_BUCKET_PICTURE_VIOLENCE,
    MINIO_BUCKET_PICTURE_RACY,
)


logger = logging.getLogger("[SERVICES AUDIO]")
logging.basicConfig(level=logging.INFO)


class AudioService:
    @staticmethod
    async def convert_audio(
        path: str, title: str, error_service: ErrorService, user_id: int
    ) -> Union[str, None]:
        try:
            out_path = UPLOAD_DIR / title
            logger.info(f"OUT_PATH: {out_path}")
            ffmpeg.input(path).output(str(out_path), ac=1).run()
            return str(out_path)

        except Exception as e:
            logger.info(f"[CONVERT] Error: {e}")
            error = ErrorCreate(
                user_id=user_id,
                message="[CONVERT AUDIO] Ошибка конвертации аудио!",
                description=str(e),
            )
            await error_service.add_one(error=error)
            return None

    @staticmethod
    async def cut_audio(
        path: str, error_service: ErrorService, user_id: int
    ) -> list[str]:
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
                    ffmpeg.input(str(path), ss=index * 30).output(
                        str(filename) + "_" + str(index + 1) + ".wav", t=30, ac=1
                    ).run()
                else:
                    ffmpeg.input(str(path), ss=index * 30).output(
                        str(filename) + "_" + str(index + 1) + ".wav", ac=1
                    ).run()

                files.append(f"{filename}_{index + 1}.wav")
                index += 1

            return files

        except Exception as e:
            logger.info(f"[CUT] Error: {e}")

            error = ErrorCreate(
                user_id=user_id,
                message="[UPLOAD AUDIO] Ошибка обработки аудио!",
                description=str(e),
            )

            await error_service.add_one(error=error)

            return files

    @staticmethod
    def speech_to_text_ru(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="ru-RU")

                return text.lower()

        except Exception as e:
            logger.info(f"[STT RU] Error: {e}")
            return " "

    @staticmethod
    def speech_to_text_en(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="en-US")

                return text.lower()

        except Exception as e:
            logger.info(f"[STT EN] Error: {e}")
            return " "

    @staticmethod
    async def upload_youtube_audio(
        link: str, error_service: ErrorService, user_id: int
    ) -> Union[Tuple[Path, str, str], Tuple[None, None, None]]:
        try:
            logger.info(link)
            uid = uuid.uuid4()
            filename_for_yt = f"audio_{uid}"
            filename = f"audio_{uid}.mp3"
            download_path_for_yt = UPLOAD_DIR / filename_for_yt
            download_path = UPLOAD_DIR / filename
            ydl_opts = {
                "format": "mp3/bestaudio/best",
                "outtmpl": "{}.%(ext)s".format(download_path_for_yt),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                    }
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(link)
                info_dict = ydl.extract_info(link, download=False)
                video_title = info_dict.get("title", None)

            return download_path, filename, video_title

        except Exception as e:
            logger.info(f"[UPLOAD YOUTUBE] Error: {e}")

            error = ErrorCreate(
                user_id=user_id,
                message="[UPLOAD YOUTUBE AUDIO] Ошибка выгрузки аудио из ютуба!",
                description=str(e),
            )

            await error_service.add_one(error=error)
            return None, None, None

    @staticmethod
    async def word_to_speech(word: str) -> Union[str, None]:
        try:
            tts = gTTS(text=word, lang="en", slow=False)

            bytes_file = BytesIO()
            tts.write_to_fp(bytes_file)
            bytes_file.seek(0)

            object_name = f'{"_".join(word.lower().split())}.mp3'

            await MinioUploader.upload_object(
                bucket_name=MINIO_BUCKET_VOICEOVER,
                object_name=object_name,
                data=bytes_file,
                lenght=bytes_file.getbuffer().nbytes,
                type="audio/mpeg",
            )

            return f"{MINIO_HOST}/{MINIO_BUCKET_VOICEOVER}/{object_name}"

        except BaseException as e:
            logger.info(f"[TTS] Error: {e}")
            return None

    @staticmethod
    async def download_picture(
        word: str,
    ) -> Union[str, None]:
        try:
            image_data = await ImageDownloader.get_image_data(word=word)

            bytes_file = BytesIO(image_data)
            bytes_file.seek(0)

            is_safe, annotations = await ImageSafetyVision.check_image_safety(
                image_content=image_data
            )

            object_name = f'{"_".join(word.lower().split())}.jpg'

            if is_safe:

                await MinioUploader.upload_object(
                    bucket_name=MINIO_BUCKET_PICTURE,
                    object_name=object_name,
                    data=bytes_file,
                    lenght=bytes_file.getbuffer().nbytes,
                    type="image/jpeg",
                )

                return f"{MINIO_HOST}/{MINIO_BUCKET_PICTURE}/{object_name}"

            for annotation in annotations:
                match annotation["type"]:
                    case ImageAnnotations.adult.value:
                        bucket_name = MINIO_BUCKET_PICTURE_ADULT
                    case ImageAnnotations.medical.value:
                        bucket_name = MINIO_BUCKET_PICTURE_MEDICAL
                    case ImageAnnotations.violence.value:
                        bucket_name = MINIO_BUCKET_PICTURE_VIOLENCE
                    case ImageAnnotations.racy.value:
                        bucket_name = MINIO_BUCKET_PICTURE_RACY

                annotation_value = annotation["value"]

                object_name = f'{annotation_value}-{"_".join(word.lower().split())}.jpg'

                await MinioUploader.upload_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    data=bytes_file,
                    lenght=bytes_file.getbuffer().nbytes,
                    type="image/jpeg",
                )

                link = f"{MINIO_HOST}/{bucket_name}/{object_name}"

                logger.info(f"[IMAGE SAFETY] Image not safety: {link}")
                return None

        except BaseException as e:
            logger.info(f"[DOWNLOAD PICTURE] Error: {e}")
            return None, None
