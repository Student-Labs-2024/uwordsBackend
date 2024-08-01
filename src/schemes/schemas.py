import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, EmailStr, field_validator


class Audio(BaseModel):
    filename: str = Field(examples=["audio_2024-05-21_23-48-47.ogg"])
    extension: str = Field(examples=[".ogg"])
    filepath: Union[str, Path] = Field(
        examples=[
            "audio_transfer/audio_6515bf33-e63c-4493-b29d-55f2b70a892d_converted.wav"
        ]
    )
    uploaded_at: datetime = Field(examples=["2024-05-26T10:10:21.520492"])


class YoutubeLink(BaseModel):
    link: str = Field(
        examples=["https://www.youtube.com/shorts/of3729gHjNs?feature=share"]
    )


class WordsIdsSchema(BaseModel):
    words_ids: list[int] = Field(examples=[[1, 2, 3]])


class WordDumpSchema(BaseModel):
    id: int = Field(examples=[1])
    enValue: str = Field(examples=["Apple"])
    ruValue: str = Field(examples=["Яблоко"])
    topic: Optional[str] = Field(examples=["Fruit"])
    subtopic: Optional[str] = Field(examples=["Oranges"])
    audioLink: Optional[str] = Field(
        examples=["https://big-nose.ru:9100/uwords-voiceover/apple.mp3"], default=None
    )
    pictureLink: Optional[str] = Field(
        examples=["https://big-nose.ru:9100/uwords-picture/apple.jpg"], default=None
    )

    class ConfigDict:
        from_attributes = True


class UserWordDumpSchema(BaseModel):
    topic: str = Field(examples=[1])
    word: WordDumpSchema
    user_id: int = Field(examples=["ijembbp53kbtSJ7FW3k68XQwJYp1"])
    frequency: int = Field(examples=[7])
    progress: int = Field(examples=[2])

    class ConfigDict:
        from_attributes = True


class TopicCreate(BaseModel):
    title: str = Field(examples=["Animal"])

    class ConfigDict:
        from_attributes = True


class SubTopicCreate(BaseModel):
    title: str = Field(examples=["Rat"])

    class ConfigDict:
        from_attributes = True


class SubTopicCreateDB(BaseModel):
    title: str = Field(examples=["Rat"])
    topic_title: str = Field(examples=["Animal"])


class SubTopicIcon(BaseModel):
    pictureLink: Optional[str] = Field(
        examples=["https://app.big-nose.ru/subtopic_icon.svg"], default=None
    )


class SubtopicWords(BaseModel):
    title: str
    word_count: int
    progress: float

    class ConfigDict:
        from_attributes = True


class TopicWords(BaseModel):
    title: str
    subtopics: List[SubtopicWords]

    class ConfigDict:
        from_attributes = True


class ErrorCreate(BaseModel):
    user_id: int = Field(examples=[1])
    message: str = Field(examples=["Ошибка обработки списка слов"])
    description: Optional[str] = Field(
        examples=["IndexError: list index out of range"], default=None
    )


class ErrorDump(BaseModel):
    id: int = Field(examples=[1])
    user_id: int = Field(examples=[1])
    message: str = Field(examples=["Ошибка обработки списка слов"])
    description: Optional[str] = Field(
        examples=["Ошибка обработки списка слов"], default=None
    )
    created_at: datetime = Field(examples=["2024-07-18 10:30:45.999999"])
    is_send: bool = Field(examples=[True])


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
    created_at: datetime = Field(examples=["2024-07-18 10:30:45.999999"])


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


class AdminEmailLogin(BaseModel):
    email: EmailStr = Field(examples=["support@uwords.ru"])
    password: Optional[str] = Field(examples=["adminstrongpass"], default=None)


class TokenInfo(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJ..."])
    refresh_token: Optional[str] = Field(examples=["eyJhbGciOiJ..."], default=None)
    token_type: str = "Bearer"


class CustomResponse(BaseModel):
    status_code: int = Field(examples=[200])
    message: str = Field(examples=["User banned successfully!"])


class AdminCreate(BaseModel):
    email: EmailStr = Field(examples=["support@uwords.ru"])
    password: str = Field(examples=["adminstrongpass"])
    admin_secret: str = Field(examples=["admin_secret"])

    @field_validator("*", mode="before")
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class SendEmailCode(BaseModel):
    email: EmailStr = Field(examples=["mail@uwords.ru"])
    code: str = Field(examples=["Wh18QI"])


class Subscription(BaseModel):
    name: str = Field(examples=["Premium"])
    price: int = Field(examples=[1500])
    months: int = Field(examples=[6])

class SubscriptionUpdate(BaseModel):
    price: int = Field(examples=[1500])
    months: int = Field(examples=[6])
    old_price: Optional[int] = Field(examples=[1500])

class SubscriptionDump(Subscription):
    id: int = Field(examples=[1])
    old_price: Optional[int] = Field(examples=[1500])
