import string
import secrets


def generate_email_verification_code(length: int) -> str:
    characters = string.digits
    code = "".join(secrets.choice(characters) for _ in range(length))
    return code


def generate_telegram_verification_code(length: int) -> str:
    characters = string.ascii_letters + string.digits
    code = "".join(secrets.choice(characters) for _ in range(length))
    return code
