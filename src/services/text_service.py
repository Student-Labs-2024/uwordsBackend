import string
import logging
from typing import Union, List, Dict
from deep_translator.google import GoogleTranslator

from src.schemes.error_schemas import ErrorCreate
from src.services.error_service import ErrorService
from src.services.services_config import ma, STOPWORDS


logger = logging.getLogger("[SERVICES TEXT]")
logging.basicConfig(level=logging.INFO)


class TextService:
    @staticmethod
    async def remove_spec_chars(
        text: str, error_service: ErrorService, user_id: int
    ) -> Union[str, None]:
        try:
            spec_chars = string.punctuation + "\n\xa0«»\t—…" + string.digits
            text_without_spec_chars = "".join(
                [char for char in text if char not in spec_chars]
            )
            return " ".join(text_without_spec_chars.split())

        except Exception as e:
            logger.info(f"[SPEC CHARS] Error: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[REMOVE SPEC CHAR]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    async def remove_stop_words(
        text: str, error_service: ErrorService, user_id: int
    ) -> Union[List[str], None]:
        try:
            return [word for word in text.split() if word not in STOPWORDS]

        except Exception as e:
            logger.info(f"[REMOVE STOPS] Error: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[REMOVE STOP WORDS]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    @staticmethod
    async def normalize_words(
        words: List[str], error_service: ErrorService, user_id: int
    ) -> Union[List[str], None]:
        try:
            norm_words = []

            for word in words:
                norm_words.append(ma.parse(word)[0].normal_form)

            return norm_words

        except Exception as e:
            logger.info(f"[NORM WORDS] Error: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[NORM WORDS]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    @staticmethod
    async def create_freq_dict(
        words: List[str], error_service: ErrorService, user_id: int
    ) -> Union[Dict[str, int], None]:
        try:
            freq_dict = {}

            for word in words:
                if word not in freq_dict.keys():
                    freq_dict[word] = 1
                else:
                    freq_dict[word] += 1

            return dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True))

        except Exception as e:
            logger.info(f"[CREATE FREQ] Error: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    @staticmethod
    async def translate(
        words: Dict,
        from_lang: str,
        to_lang: str,
        error_service: ErrorService,
        user_id: int,
    ) -> List[Dict[str, Union[str, int]]]:

        translated_words = []

        for word in words.keys():
            word: str
            try:
                translated = GoogleTranslator(
                    source=from_lang, target=to_lang
                ).translate(word)

                if not translated:
                    continue

                if from_lang == "russian":
                    translated_words.append(
                        {
                            "ruValue": word.capitalize(),
                            "enValue": translated.capitalize(),
                            "frequency": words[word],
                        }
                    )

                else:
                    translated_words.append(
                        {
                            "ruValue": translated.capitalize(),
                            "enValue": word.capitalize(),
                            "frequency": words[word],
                        }
                    )

            except Exception as e:
                logger.info(f"[TRANSLATE] Error: {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[TRANSLATE]", description=str(e)
                )

                await error_service.add_one(error=error)
                continue

        return translated_words
