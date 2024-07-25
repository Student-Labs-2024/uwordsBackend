from check_swear import SwearingCheck
from better_profanity import profanity


class CensoreFilter:
    def __init__(self):
        self.swear_check = SwearingCheck()
        profanity.load_censor_words()

    def is_censore(self, text: str) -> bool:
        if self.swear_check.predict(text)[0]:
            return True
        if profanity.contains_profanity(text):
            return True
        return False

    def replace(self, text: str, replRU: str = "****", replEN: str = "*") -> str:
        text = profanity.censor(text, replEN)
        words = text.split()
        censored_words = []
        for word in words:
            if self.swear_check.predict(word)[0]:
                censored_words.append(replRU)
            else:
                censored_words.append(word)
        return " ".join(censored_words)
