import ssl
import smtplib
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import HTTPException, status

from src.database.redis_config import redis_connection
from src.utils.email import generate_email_verification_code

from src.config.instance import (
    EMAIL_CODE_ATTEMPTS,
    EMAIL_PASSWORD,
    SENDER_EMAIL,
    EMAIL_PORT,
    SMTP_SERVER,
    EMAIL_CODE_LEN,
)


class EmailService:
    @staticmethod
    def generate_code(code_len=EMAIL_CODE_LEN) -> str:
        return generate_email_verification_code(code_len)

    @staticmethod
    def check_code(email: EmailStr, code: str) -> bool:
        try:
            codes_db: str = redis_connection.get(email).decode("utf-8")
            attempts: bytes = redis_connection.get(email + "attempts")

            if attempts:
                attempts: int = int(attempts.decode("utf-8"))

            else:
                attempts: int = 1

            if attempts > int(EMAIL_CODE_ATTEMPTS):
                redis_connection.delete(*[email, email + "attempts"])

                raise HTTPException(
                    detail="Too many attempts",
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                )

            for code_db in codes_db.split():
                if code_db == code:
                    return True

            redis_connection.set(email + "attempts", attempts + 1)
            return False

        except AttributeError:
            raise HTTPException(
                detail="No code for this email", status_code=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def send_email(email: str, theme: str, text: str) -> None:
        context = ssl.create_default_context()

        message = MIMEMultipart("alternative")

        message["Subject"] = theme
        message["From"] = SENDER_EMAIL
        message["To"] = email

        message.attach(MIMEText(text, "plain"))

        with smtplib.SMTP_SSL(SMTP_SERVER, int(EMAIL_PORT), context=context) as server:
            server.login(user=SENDER_EMAIL, password=EMAIL_PASSWORD)
            server.sendmail(
                from_addr=SENDER_EMAIL, to_addrs=email, msg=message.as_string()
            )
