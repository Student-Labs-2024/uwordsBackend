import os
import uuid
import json
import ffmpeg
import logging
import aiohttp
import requests
from gtts import gTTS
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Tuple, List
from speech_recognition import AudioFile

from src.schemes.error_schemas import ErrorCreate
from src.services.services_config import sr
from src.services.error_service import ErrorService
from src.services.minio_uploader import MinioUploader

from src.config.instance import (
    HUGGING_FACE_TOKEN,
    HUGGING_FACE_URL,
    MINIO_BUCKET_VOICEOVER,
    MINIO_HOST,
    UPLOAD_DIR,
    DOWNLOADER_URL,
    DOWNLOADER_TOKEN,
)


logger = logging.getLogger("[SERVICES AUDIO]")
logging.basicConfig(level=logging.INFO)


class AudioService:
    @staticmethod
    async def convert_audio(
        path: str, title: str, error_service: ErrorService, user_id: int
    ) -> Union[str, None]:
        try:
            out_path = UPLOAD_DIR / f"{title}_converted.wav"
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
        path: str,
        error_service: ErrorService,
        user_id: int,
        duration: int,
        allowed_iterations: Optional[int] = None,
    ) -> List[str]:
        files = []

        try:
            index = 0

            while index * 30 < duration:
                if allowed_iterations:
                    if index > allowed_iterations:
                        break

                filename, _ = os.path.splitext(path)

                outpath = f"{filename}_{index + 1}.wav"

                logger.info(f"[AUDIO] path: {path} new_path: {outpath}")

                if (index + 1) * 30 < duration:
                    ffmpeg.input(str(path), ss=index * 30).output(
                        str(outpath), t=30, ac=1
                    ).run()
                else:
                    ffmpeg.input(str(path), ss=index * 30).output(
                        str(outpath), ac=1
                    ).run()

                files.append(outpath)
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
    def speech_to_text(filepath: str) -> str:
        try:
            with open(file=filepath, mode="rb") as audio:
                audio_data = audio.read()

            response = requests.post(
                url=HUGGING_FACE_URL,
                headers={
                    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                },
                data=audio_data,
            )

            if response.status_code != 200:
                logger.info(f"[STT HF] Error: {response.text}")

            data: dict = json.loads(response.text)

            return data.get("text")

        except Exception as e:
            logger.info(f"[STT HF] Error: {e}")
            return " "

    @staticmethod
    def speech_to_text_ru(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="ru-RU")

                return text.lower()

        except Exception as e:
            return " "

    @staticmethod
    def speech_to_text_en(filepath: str) -> str:
        try:
            with AudioFile(filepath) as source:
                audio_data = sr.record(source)
                text = sr.recognize_google(audio_data, language="en-US")

                return text.lower()

        except Exception as e:
            return " "

    @staticmethod
    async def upload_youtube_audio(
        link: str, error_service: ErrorService, user_id: int
    ) -> Union[Tuple[Path, str], Tuple[None, None]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=f"{DOWNLOADER_URL}/api/v1/youtube/download",
                    params={"link": link},
                    headers={"Authorization": f"Bearer {DOWNLOADER_TOKEN}"},
                ) as response:
                    response.raise_for_status()

                    uid = uuid.uuid4()
                    file_name = f"audio_{uid}.mp3"
                    upload_path = UPLOAD_DIR / file_name

                    with open(file=upload_path, mode="wb") as f:
                        while True:
                            chunk = await response.content.read()
                            if not chunk:
                                break
                            f.write(chunk)

                    return upload_path, file_name

        except Exception as e:
            logger.info(f"[UPLOAD YOUTUBE] Error: {e}")

            error = ErrorCreate(
                user_id=user_id,
                message="[UPLOAD YOUTUBE AUDIO] Ошибка выгрузки аудио из ютуба!",
                description=str(e),
            )

            await error_service.add_one(error=error)
            return None, None

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
