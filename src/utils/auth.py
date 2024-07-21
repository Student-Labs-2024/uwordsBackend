import json
import bcrypt
import logging
import requests
from enum import Enum
from jwt import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database.models import User
from src.config.instance import SERVICE_TOKEN

from src.services.user_service import UserService

from src.utils import tokens as token_utils
from src.utils.dependenes.user_service_fabric import user_service_fabric


logger = logging.getLogger("[AUTH UTILS]")
logging.basicConfig(level=logging.INFO)

http_bearer = HTTPBearer()


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password_bytes: bytes = password.encode()
    return bcrypt.hashpw(password=password_bytes, salt=salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    password_bytes: bytes = password.encode()
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_password)


async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    token = credentials.credentials

    try:
        payload: dict = token_utils.decode_jwt(token=token)

        return payload

    except InvalidTokenError as e:
        logger.info(f"[USER TOKEN] ERROR: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail={"msg": "Invalid token"}
        )


async def validate_token(payload: dict, token_type: str) -> bool:
    current_token_type: str = payload.get("type")

    if current_token_type != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": f"Invalid token type: '{current_token_type}' | expected: '{token_type}'"
            },
        )

    return True


async def get_user_by_token(
    payload: dict, user_service: UserService = user_service_fabric()
) -> User:
    user_id: int | None = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": f"User with ID {user_id} not found"},
        )

    user = await user_service.get_user_by_id(user_id=user_id)
    return user


async def get_current_user(
    payload: dict = Depends(get_current_token_payload),
) -> User:
    await validate_token(payload=payload, token_type="access")
    return await get_user_by_token(payload=payload)


async def get_current_user_by_refresh(
    payload: dict = Depends(get_current_token_payload),
) -> User:
    await validate_token(payload=payload, token_type="refresh")
    return await get_user_by_token(payload=payload)


async def get_active_current_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": f"User {user.email} banned"},
        )

    return user


async def get_admin_user(user: User = Depends(get_active_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": f"User {user.email} not a superuser"},
        )

    return user


async def validate_vk_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    token = credentials.credentials
    service_token = SERVICE_TOKEN
    res = requests.get(
        f"https://api.vk.com/method/secure.checkToken?v=5.199&token={token}",
        headers={"Authorization": f"Bearer {service_token}"},
    )
    response = json.loads(res.content.decode("utf-8"))
    try:
        if response["response"]:
            return response
    except KeyError:
        raise HTTPException(
            detail="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
        )


class Providers(Enum):
    email = "email"
    vk = "vk"
    google = "google"
    admin = "admin"
