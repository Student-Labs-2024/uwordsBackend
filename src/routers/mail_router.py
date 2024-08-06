from fastapi import APIRouter

from src.celery.tasks import send_email_task
from src.schemes.util_schemas import SendEmailCode
from src.services.email_service import EmailService
from src.database.redis_config import redis_connection

from src.config.instance import EMAIL_CODE_EXP
from src.config import fastapi_docs_config as doc_data


mail_router_v1 = APIRouter(prefix="/api/email", tags=["Email"])


@mail_router_v1.get(
    "/send_code",
    response_model=str,
    name=doc_data.SEND_CODE_TITLE,
    description=doc_data.SEND_CODE_DESCRIPTION,
)
async def get_code_on_email(user_email: str) -> str:
    code = EmailService.generate_code()
    redis_connection.set(user_email, code, ex=int(EMAIL_CODE_EXP))
    send_email_task.apply_async((user_email, code), countdown=1)
    return "Code is sent"


@mail_router_v1.post(
    "/check_code",
    response_model=bool,
    name=doc_data.CHECK_CODE_TITLE,
    description=doc_data.CHECK_CODE_DESCRIPTION,
)
async def check_code(data: SendEmailCode) -> bool:
    return EmailService.check_code(data.email, data.code)
