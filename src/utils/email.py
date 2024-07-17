import secrets
import string


def generate_verification_code(length: int) -> str:
    characters = string.ascii_letters + string.digits
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code
