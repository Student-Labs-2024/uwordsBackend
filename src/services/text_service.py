import string
from typing import Union, List, Dict
from deep_translator.google import GoogleTranslator
from src.schemes.error_schemas import ErrorCreate
from src.services.error_service import ErrorService
from src.services.services_config import (
    ma,
    device,
    STOPWORDS,
    model_en_ru,
    model_ru_en,
    tokenizer_en_ru,
    tokenizer_ru_en,
)
from langdetect import detect
from src.utils.logger import text_service_logger


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
            text_service_logger.error(f"[SPEC CHARS] Error: {e}")

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
            text_service_logger.error(f"[REMOVE STOPS] Error: {e}")

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
            text_service_logger.error(f"[NORM WORDS] Error: {e}")

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
            text_service_logger.error(f"[CREATE FREQ] Error: {e}")

            error = ErrorCreate(
                user_id=user_id, message="[CREATE FREQ]", description=str(e)
            )

            await error_service.add_one(error=error)
            return None

    @staticmethod
    async def get_translated_clear_text(text, error_service, user_id):
        text_language = detect(text=text)

        text_without_spec_chars = await TextService.remove_spec_chars(
            text=text, error_service=error_service, user_id=user_id
        )

        words = await TextService.remove_stop_words(
            text=text_without_spec_chars,
            error_service=error_service,
            user_id=user_id,
        )

        norm_words = await TextService.normalize_words(
            words=words, error_service=error_service, user_id=user_id
        )

        freq_dict = await TextService.create_freq_dict(
            words=norm_words, error_service=error_service, user_id=user_id
        )

        if text_language == "ru":
            translated_words = await TextService.translate_ru_en(
                words=freq_dict, error_service=error_service, user_id=user_id
            )

        else:
            translated_words = await TextService.translate_en_ru(
                words=freq_dict, error_service=error_service, user_id=user_id
            )

        return translated_words

    @staticmethod
    async def translate_en_ru(
        words: Dict[str, int],
        error_service: ErrorService,
        user_id: int,
    ) -> List[Dict[str, Union[str, int]]]:
        translated_words = []

        for word in words:
            try:
                inputs = tokenizer_en_ru(word, return_tensors="pt", padding=True).to(device)

                translated = model_en_ru.generate(
                    **inputs, max_length=50, num_beams=5, no_repeat_ngram_size=2
                )

                translated_text: str = tokenizer_en_ru.decode(
                    translated[0],
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )

                translated_text = translated_text.replace(".", "")

                data = {
                    "ruValue": translated_text.capitalize(),
                    "enValue": word.capitalize(),
                    "frequency": words[word],
                }

                translated_words.append(data)

                text_service_logger.info(
                    f"[TRANSLATE] EN: {word} -> RU: {translated_text}"
                )

            except Exception as e:
                text_service_logger.error(f"[TRANSLATE] Error: {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[TRANSLATE]", description=str(e)
                )

                await error_service.add_one(error=error)
                continue

        return translated_words

    @staticmethod
    async def translate_ru_en(
        words: Dict[str, int],
        error_service: ErrorService,
        user_id: int,
    ) -> List[Dict[str, Union[str, int]]]:
        translated_words = []

        for word in words:
            try:
                inputs = tokenizer_ru_en(word, return_tensors="pt", padding=True).to(device)

                translated = model_ru_en.generate(
                    **inputs, max_length=50, num_beams=5, no_repeat_ngram_size=2
                )

                translated_text: str = tokenizer_ru_en.decode(
                    translated[0],
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )

                translated_text = translated_text.replace(".", "")

                data = {
                    "ruValue": word.capitalize(),
                    "enValue": translated_text.capitalize(),
                    "frequency": words[word],
                }

                translated_words.append(data)

                text_service_logger.info(
                    f"[TRANSLATE] RU: {word} -> EN: {translated_text}"
                )

            except Exception as e:
                text_service_logger.error(f"[TRANSLATE] Error: {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[TRANSLATE]", description=str(e)
                )

                await error_service.add_one(error=error)
                continue

        return translated_words

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
                text_service_logger.error(f"[TRANSLATE] Error: {e}")

                error = ErrorCreate(
                    user_id=user_id, message="[TRANSLATE]", description=str(e)
                )

                await error_service.add_one(error=error)
                continue

        return translated_words
