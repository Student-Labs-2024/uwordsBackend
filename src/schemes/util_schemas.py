from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class TokenInfo(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJ..."])
    refresh_token: Optional[str] = Field(examples=["eyJhbGciOiJ..."], default=None)
    token_type: str = "Bearer"


class CustomResponse(BaseModel):
    status_code: int = Field(examples=[200])
    message: str = Field(examples=["User banned successfully!"])


class SendEmailCode(BaseModel):
    email: EmailStr = Field(examples=["mail@uwords.ru"])
    code: str = Field(examples=["Wh18QI"])


class TelegramCode(BaseModel):
    code: str = Field(examples=["Wh18QI"])


class Bill(BaseModel):
    id: int = Field(examples=[1])
    label: str = Field(examples=["1568642313854321354321543561"])
    sub_type: int = Field(examples=[9])
    amount: int = Field(examples=[1500])
    success: bool = Field(examples=[False])
