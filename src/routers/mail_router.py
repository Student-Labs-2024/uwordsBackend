from pydantic import EmailStr
from email_validator import validate_email, EmailNotValidError

from fastapi import APIRouter, Depends, HTTPException, status

from src.celery.tasks import send_email_task
from src.schemes.util_schemas import SendEmailCode
from src.services.email_service import EmailService
from src.database.redis_config import redis_connection

from src.config.instance import EMAIL_CODE_EXP
from src.config import fastapi_docs_config as doc_data

from src.utils.auth import check_secret_token


mail_router_v1 = APIRouter(prefix="/api/email", tags=["Email"])


@mail_router_v1.get(
    "/send_code",
    response_model=str,
    name=doc_data.SEND_CODE_TITLE,
    description=doc_data.SEND_CODE_DESCRIPTION,
)
async def get_code_on_email(
    user_email: EmailStr, token=Depends(check_secret_token)
) -> str:
    try:
        validate_email(user_email)
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Not valid email"}
        )

    code = EmailService.generate_code()
    try:
        codes_db: str = redis_connection.get(user_email).decode("utf-8")
        codes_db += f" {code}"
    except:
        codes_db = code

    redis_connection.set(user_email, codes_db, ex=int(EMAIL_CODE_EXP))
    send_email_task.apply_async((user_email, code), countdown=1)
    return "Code is sent"


@mail_router_v1.post(
    "/check_code",
    response_model=bool,
    name=doc_data.CHECK_CODE_TITLE,
    description=doc_data.CHECK_CODE_DESCRIPTION,
)
async def check_code(data: SendEmailCode, token=Depends(check_secret_token)) -> bool:
    return EmailService.check_code(data.email, data.code)
