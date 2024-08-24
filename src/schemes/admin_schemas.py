from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class AdminEmailLogin(BaseModel):
    email: EmailStr = Field(examples=["support@uwords.ru"])
    password: Optional[str] = Field(examples=["adminstrongpass"], default=None)


class AdminCreate(BaseModel):
    email: EmailStr = Field(examples=["support@uwords.ru"])
    password: str = Field(examples=["adminstrongpass"])
    admin_secret: str = Field(examples=["admin_secret"])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class BotWords(BaseModel):
    uwords_uid: str = Field(examples=["1"])
    text: str = Field(examples=["word"])
