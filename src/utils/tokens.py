import jwt
from typing import Dict
from datetime import datetime, timedelta

from src.database.models import User

from src.config.instance import (
    JWT_ALGORITHM,
    JWT_SECRET,
    ACCESS_TOKEN_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
)


def encode_jwt(
    payload: Dict,
    key: str = JWT_SECRET,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    datetime_now = datetime.now()

    to_payload = payload.copy()

    token_type: str = payload.get("type")

    if token_type == "access":
        expired_at = datetime_now + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    elif token_type == "refresh":
        expired_at = datetime_now + timedelta(days=REFRESH_TOKEN_LIFETIME)

    to_payload.update({"iat": datetime_now.timestamp(), "exp": expired_at.timestamp()})

    encoded = jwt.encode(payload=to_payload, key=key, algorithm=algorithm)

    return encoded


def decode_jwt(
    token: str, key: str = JWT_SECRET, algorithm: str = JWT_ALGORITHM
) -> Dict:

    decode = jwt.decode(jwt=token, key=key, algorithms=[algorithm])

    return decode


def create_jwt(token_type: str, payload: Dict) -> str:

    jwt_payload = {"type": token_type}
    jwt_payload.update(payload)

    return encode_jwt(payload=jwt_payload)


def create_access_token(user: User) -> str:
    jwt_payload = {"sub": "user", "user_id": user.id, "email": user.email}

    return create_jwt(token_type="access", payload=jwt_payload)


def create_refresh_token(user: User) -> str:
    jwt_payload = {"sub": "user", "user_id": user.id}

    return create_jwt(token_type="refresh", payload=jwt_payload)
