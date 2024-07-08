import asyncio
import logging
import string
from deep_translator.google import GoogleTranslator
from src.schemes.schemas import ErrorCreate
from src.services.services_config import ma, STOPWORDS

logger = logging.getLogger("[SERVICES FILE]")
logging.basicConfig(level=logging.INFO)


class TextService:
    @staticmethod
    def get_frequency_dict(text: str, error_service, user_id) -> dict:
        try:
            text_without_spec_chars = TextService.remove_spec_chars(text=text)

            words = TextService.remove_stop_words(text=text_without_spec_chars)

            norm_words = TextService.normalize_words(words=words)

            freq_dict = TextService.create_freq_dict(words=norm_words)

            return freq_dict
        
        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[GET FREQ]",
                description=str(e)
            )
            error_obj = asyncio.run(error_service.add(error=error))
            logger.info(error_obj)
            return None

        

    @staticmethod
    def remove_spec_chars(text: str, error_service, user_id: str) -> str:
        try:
            spec_chars = string.punctuation + '\n\xa0«»\t—…' + '0123456789'
            return "".join([char for char in text if char not in spec_chars])

        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[REMOVE SPEC CHAR]",
                description=str(e)
            )
            error_obj = asyncio.run(error_service.add(error=error))
            logger.info(error_obj)
            return None
        
        

    @staticmethod
    def normalize_words(words: list[str], error_service, user_id: str) -> list[str]:
        try:
            norm_words = []

            for word in words:
                norm_words.append(ma.parse(word)[0].normal_form)

            return norm_words
        
        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[NORM WORDS]",
                description=str(e)
            )
            error_obj = asyncio.run(error_service.add(error=error))
            logger.info(error_obj)
            return None

    @staticmethod
    def create_freq_dict(words: list[str], error_service, user_id: str) -> dict:
        try:
            freq_dict = {}

            for word in words:
                if word not in freq_dict.keys():
                    freq_dict[word] = 1
                else:
                    freq_dict[word] += 1

            return dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True))
        
        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[CREATE FREQ]",
                description=str(e)
            )
            error_obj = asyncio.run(error_service.add(error=error))
            logger.info(error_obj)
            return None

    def remove_stop_words(text: str, error_service, user_id: str) -> list[str]:
        try:
            return [word for word in text.split() if word not in STOPWORDS]
        
        except Exception as e:
            logger.info(e)
            error = ErrorCreate(
                user_id=user_id,
                message="[REMOVE STOP WORDS]",
                description=str(e)
            )
            error_obj = asyncio.run(error_service.add(error=error))
            logger.info(error_obj)
            return None

    @staticmethod
    def translate(words: dict, from_lang: str, to_lang: str, error_service, user_id: str) -> list[dict]:

        translated_words = []

        for word in words.keys():
            word: str
            try:
                translated = GoogleTranslator(source=from_lang, target=to_lang).translate(word)

                if from_lang == "russian":
                    translated_words.append({
                        'ruValue': word.capitalize(),
                        'enValue': translated.capitalize(),
                        'frequency': words[word]
                    })

                else:
                    translated_words.append({
                        'ruValue': translated.capitalize(),
                        'enValue': word.capitalize(),
                        'frequency': words[word]
                    })

            except Exception as e:
                logger.info(e)
                error = ErrorCreate(
                    user_id=user_id,
                    message="[TRANSLATE]",
                    description=str(e)
                )
                error_obj = asyncio.run(error_service.add(error=error))
                logger.info(error_obj)
                continue

        return translated_words
