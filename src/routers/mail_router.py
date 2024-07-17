from fastapi import APIRouter
from src.config.instance import EMAIL_CODE_EXP
from src.database.redis_config import redis_connection
from src.schemes.schemas import SendEmailCode
from src.services.email_service import EmailService
from src.celery.tasks import send_email_task

mail_router_v1 = APIRouter(prefix="/api/email", tags=["Email"])


@mail_router_v1.get('/send_code', response_model=str)
async def get_code_on_email(user_email: str) -> str:
    code = EmailService.generate_code()
    redis_connection.set(user_email, code, ex=int(EMAIL_CODE_EXP))
    send_email_task.apply_async((user_email, code), countdown=1)
    return "Code is sent"


@mail_router_v1.post('/check_code', response_model=bool)
async def check_code(data: SendEmailCode) -> bool:
    return EmailService.check_code(data.email, data.code)
