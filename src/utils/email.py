import string
import secrets


def generate_verification_code(characters: str, length: int) -> str:
    code = "".join(secrets.choice(characters) for _ in range(length))
    return code


def generate_email_verification_code(length: int) -> str:
    characters = string.digits
    return generate_verification_code(characters, length)


def generate_telegram_verification_code(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return generate_verification_code(characters, length)
