import bcrypt


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password=password_bytes, salt=salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    password_bytes: bytes = password.encode()
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_password)
