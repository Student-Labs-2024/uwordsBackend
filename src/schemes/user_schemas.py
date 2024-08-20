import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from src.schemes.achievement_schemas import UserAchievementDump
from src.schemes.word_schemas import WordDumpSchema


class UserWordDumpSchema(BaseModel):
    topic: str = Field(examples=[1])
    word: WordDumpSchema
    user_id: int = Field(examples=["ijembbp53kbtSJ7FW3k68XQwJYp1"])
    frequency: int = Field(examples=[7])
    progress: int = Field(examples=[2])

    class ConfigDict:
        from_attributes = True


class UserDump(BaseModel):
    id: int = Field(examples=[1])
    email: Optional[EmailStr] = Field(examples=["mail@uwords.ru"], default=None)
    provider: str = Field(examples=["email"])
    google_id: Optional[str] = Field(examples=["uid34840..."], default=None)
    vk_id: Optional[str] = Field(examples=["id6473..."], default=None)
    username: Optional[str] = Field(examples=["uwords"], default=None)
    firstname: Optional[str] = Field(examples=["Uwords"], default=None)
    lastname: Optional[str] = Field(examples=["English App"], default=None)
    avatar_url: Optional[str] = Field(
        examples=["https://uwords.ru/image/logo.png"], default=None
    )
    latest_study: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"], default=None
    )
    days: Optional[int] = Field(examples=[0])
    phone_number: Optional[str] = Field(examples=["88005553535"], default=None)
    birth_date: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"], default=None
    )
    subscription_type: Optional[int] = Field(examples=[1])
    subscription_acquisition: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"]
    )
    subscription_expired: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"]
    )
    allowed_audio_seconds: Optional[int] = Field(examples=[1800])
    allowed_video_seconds: Optional[int] = Field(examples=[900])
    energy: Optional[int] = Field(examples=[100])
    created_at: datetime = Field(examples=["2024-07-18 10:30:45.999999"])
    metrics: Optional[dict] = Field(
        examples=[{"hours": 10, "learned": 50, "days": 5}],
        default={"hours": 0, "learned": 0, "days": 0},
    )
    achievements: List[UserAchievementDump] = Field(examples=[], default=[])

    class ConfigDict:
        from_attributes = True


class UserCreateEmail(BaseModel):
    password: str = Field(examples=["strongpass"])
    code: str = Field(examples=["Wh18QI"])
    email: EmailStr = Field(examples=["mail@uwords.ru"])
    username: Optional[str] = Field(examples=["uwords"])
    birth_date: str = Field(examples=["2023-05-05 10:30:45.999999"])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserCreateVk(BaseModel):
    firstname: str = Field(examples=["Uwords"])
    lastname: str = Field(examples=["English App"])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserCreateGoogle(BaseModel):
    google_id: str = Field(examples=[uuid.uuid4()])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserGoogleLogin(BaseModel):
    google_id: str = Field(examples=[uuid.uuid4()])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserCreateDB(BaseModel):
    provider: str = Field(examples=["email"])
    email: Optional[EmailStr] = Field(examples=["mail@uwords.ru"], default=None)
    hashed_password: Optional[str] = Field(
        examples=["43f8a2ad188263...."], default=None
    )
    google_id: Optional[str] = Field(examples=["uid34840..."], default=None)
    vk_id: Optional[str] = Field(examples=["id6473..."], default=None)
    username: Optional[str] = Field(examples=["uwords"], default=None)
    firstname: Optional[str] = Field(examples=["Uwords"], default=None)
    lastname: Optional[str] = Field(examples=["English App"], default=None)
    avatar_url: Optional[str] = Field(
        examples=["https://uwords.ru/image/logo.png"], default=None
    )
    phone_number: Optional[str] = Field(examples=["88005553535"], default=None)
    birth_date: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"], default=None
    )
    latest_study: Optional[datetime] = Field(
        examples=["2023-05-05 10:30:45.999999"], default=None
    )
    is_active: Optional[bool] = Field(examples=[True], default=True)
    is_superuser: Optional[bool] = Field(examples=[False], default=False)
    is_verified: Optional[bool] = Field(examples=[True], default=False)

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserUpdate(BaseModel):
    username: Optional[str] = Field(examples=["uwords"], default=None)
    firstname: Optional[str] = Field(examples=["Uwords"], default=None)
    lastname: Optional[str] = Field(examples=["English App"], default=None)
    avatar_url: Optional[str] = Field(
        examples=["https://uwords.ru/image/logo.png"], default=None
    )
    phone_number: Optional[str] = Field(examples=["88005553535"], default=None)
    birth_date: Optional[str] = Field(
        examples=["2023-05-05 10:30:45.999999"], default=None
    )

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserEmailLogin(BaseModel):
    email: EmailStr = Field(examples=["mail@uwords.ru"])
    password: Optional[str] = Field(examples=["strongpass"], default=None)
