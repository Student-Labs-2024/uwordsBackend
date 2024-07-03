import logging
import string
from deep_translator.google import GoogleTranslator
from src.services.services_config import ma, STOPWORDS

logger = logging.getLogger("[SERVICES FILE]")
logging.basicConfig(level=logging.INFO)


class TextService:
    @staticmethod
    def get_frequency_dict(text: str) -> dict:
        text_without_spec_chars = TextService.remove_spec_chars(text=text)

        words = TextService.remove_stop_words(text=text_without_spec_chars)

        norm_words = TextService.normalize_words(words=words)

        freq_dict = TextService.create_freq_dict(words=norm_words)

        return freq_dict

    @staticmethod
    def remove_spec_chars(text: str) -> str:
        spec_chars = string.punctuation + '\n\xa0«»\t—…' + '0123456789'
        return "".join([char for char in text if char not in spec_chars])

    @staticmethod
    def normalize_words(words: list[str]) -> list[str]:
        norm_words = []

        for word in words:
            norm_words.append(ma.parse(word)[0].normal_form)

        return norm_words

    @staticmethod
    def create_freq_dict(words: list[str]) -> dict:
        freq_dict = {}

        for word in words:
            if word not in freq_dict.keys():
                freq_dict[word] = 1
            else:
                freq_dict[word] += 1

        return dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True))

    def remove_stop_words(text: str) -> list[str]:
        return [word for word in text.split() if word not in STOPWORDS]

    @staticmethod
    def translate(words: dict, from_lang: str, to_lang: str) -> list[dict]:

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
                continue

        return translated_words
