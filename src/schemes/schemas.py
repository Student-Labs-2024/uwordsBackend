from pathlib import Path
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator

class Audio(BaseModel):
    filename: str = Field(examples=["audio_2024-05-21_23-48-47.ogg"])
    extension: str = Field(examples=[".ogg"])
    filepath: Union[str, Path] = Field(
        examples=["audio_transfer/audio_6515bf33-e63c-4493-b29d-55f2b70a892d_converted.wav"])
    uploaded_at: datetime = Field(examples=["2024-05-26T10:10:21.520492"])


class YoutubeLink(BaseModel):
    link: str = Field(examples=["https://www.youtube.com/shorts/of3729gHjNs?feature=share"])


class WordsIdsSchema(BaseModel):
    words_ids: list[int] = Field(examples=[[1, 2, 3]])


class WordDumpSchema(BaseModel):
    id: int = Field(examples=[1])
    enValue: str = Field(examples=["Apple"])
    ruValue: str = Field(examples=["Яблоко"])
    topic: Optional[str] = Field(examples=["Fruit"])
    subtopic: Optional[str] = Field(examples=["Oranges"])
    audioLink: Optional[str] = Field(examples=["https://big-nose.ru:9100/uwords-voiceover/apple.mp3"], default=None)
    pictureLink: Optional[str] = Field(examples=["https://big-nose.ru:9100/uwords-picture/apple.jpg"], default=None)

    class Config:
        from_attributes = True


class UserWordDumpSchema(BaseModel):
    topic: str = Field(examples=[1])
    word: WordDumpSchema
    user_id: int = Field(examples=["ijembbp53kbtSJ7FW3k68XQwJYp1"])
    frequency: int = Field(examples=[7])
    progress: int = Field(examples=[2])

    class Config:
        from_attributes = True


class Topic(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Animal"])

    class Config:
        from_attributes = True


class SubTopic(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Rat"])
    topic_title: str = Field(examples=['Animal'])
    class Config:
        from_attributes = True


class ErrorCreate(BaseModel):
    user_id: int
    message: str
    description: Optional[str]


class ErrorDump(BaseModel):
    id: int
    user_id: int
    message: str
    description: Optional[str]
    created_at: datetime
    is_send: bool


class UserDump(BaseModel):
    id: int
    email: EmailStr
    provider: str

    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    created_at: datetime


class UserCreate(BaseModel):
    provider: str
    email: EmailStr
    password: str

    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[str] = None

    @validator("*", pre=True)
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserCreateDB(BaseModel):
    provider: str
    email: EmailStr
    hashed_password: str

    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @validator("*", pre=True)
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserUpdate(BaseModel):
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Union[datetime, str, None] = None

    @validator("*", pre=True)
    def remove_empty(cls, value):
        if value == "":
            return None
        return value


class UserLogin(BaseModel):
    provider: str
    email: EmailStr
    password: str


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"


class CustomResponse(BaseModel):
    status_code: int
    message: str


class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    admin_secret: str

    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Union[datetime, str, None] = None

    @validator("*", pre=True)
    def remove_empty(cls, value):
        if value == "":
            return None
        return value