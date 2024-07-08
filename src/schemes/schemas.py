from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr
from fastapi_users import schemas

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
    user_id: str = Field(examples=["ijembbp53kbtSJ7FW3k68XQwJYp1"])
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

class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    firstname: str
    lastname: Optional[str] = None
    email: EmailStr
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[datetime] = None
    created_at: datetime


class UserCreate(schemas.BaseUserCreate):
    username: str
    firstname: str
    lastname: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    birth_date: Optional[str] = None

    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = True


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    avatar_url: Optional[str]
    phone_number: Optional[str]
    birth_date: Optional[datetime]

class ErrorCreate(BaseModel):
    user_id: str
    message: str
    description: Optional[str]

class ErrorDump(BaseModel):
    id: int
    user_id: str
    message: str
    description: Optional[str]
    created_at: datetime
    is_send: bool
