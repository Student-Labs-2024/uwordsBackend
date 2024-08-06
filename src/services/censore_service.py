import logging
from typing import Tuple, List, Dict
from google.cloud.vision import Image

from src.services.services_config import google_vision, profanity, swear_check
from src.config.instance import IMAGE_SAFETY_INDEX, IMAGE_SAFETY_SCALE

from src.schemes.enums.enums import ImageAnnotations


logger = logging.getLogger("[SERVICES CENSORE]")
logging.basicConfig(level=logging.INFO)


class CensoreFilter:

    @staticmethod
    def is_censore(text: str) -> bool:
        if swear_check.predict(text)[0]:
            return True
        if profanity.contains_profanity(text):
            return True
        return False

    @staticmethod
    def replace(text: str, replRU: str = "****", replEN: str = "*") -> str:
        text = profanity.censor(text, replEN)
        words = text.split()
        censored_words = []
        for word in words:
            if swear_check.predict(word)[0]:
                censored_words.append(replRU)
            else:
                censored_words.append(word)
        return " ".join(censored_words)


class ImageSafetyVision:

    @staticmethod
    async def check_image_safety(
        image_content: bytes,
    ) -> Tuple[bool, List[Dict[str, str]]]:
        image = Image(content=image_content)

        response = google_vision.safe_search_detection(image=image)
        safe = response.safe_search_annotation

        is_safe = True
        annotations = []

        if safe.adult >= IMAGE_SAFETY_INDEX:
            logger.info(f"[IMAGE SAFETY] Adult: {IMAGE_SAFETY_SCALE[safe.adult]}")
            annotations.append(
                {
                    "type": ImageAnnotations.adult.value,
                    "value": IMAGE_SAFETY_SCALE[safe.adult],
                }
            )
            is_safe = False

        if safe.medical >= IMAGE_SAFETY_INDEX:
            logger.info(f"[IMAGE SAFETY] Medical: {IMAGE_SAFETY_SCALE[safe.medical]}")
            annotations.append(
                {
                    "type": ImageAnnotations.medical.value,
                    "value": IMAGE_SAFETY_SCALE[safe.medical],
                }
            )
            is_safe = False

        if safe.violence >= IMAGE_SAFETY_INDEX:
            logger.info(f"[IMAGE SAFETY] Violence: {IMAGE_SAFETY_SCALE[safe.violence]}")
            annotations.append(
                {
                    "type": ImageAnnotations.violence.value,
                    "value": IMAGE_SAFETY_SCALE[safe.violence],
                }
            )
            is_safe = False

        if safe.racy >= IMAGE_SAFETY_INDEX:
            logger.info(f"[IMAGE SAFETY] Racy: {IMAGE_SAFETY_SCALE[safe.racy]}")
            annotations.append(
                {
                    "type": ImageAnnotations.racy.value,
                    "value": IMAGE_SAFETY_SCALE[safe.racy],
                }
            )
            is_safe = False

        return is_safe, annotations
