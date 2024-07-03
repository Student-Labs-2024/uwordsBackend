from pathlib import Path
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class Audio(BaseModel):
    filename: str = Field(examples=["audio_2024-05-21_23-48-47.ogg"])
    extension: str = Field(examples=[".ogg"])
    filepath: Union[str, Path] = Field(examples=["audio_transfer/audio_6515bf33-e63c-4493-b29d-55f2b70a892d_converted.wav"])
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
    audioLink: Optional[str] = Field(examples=["https://big-nose.ru:9100/uwords-voiceover/apple.mp3"], default=None)
    pictureLink: Optional[str] = Field(examples=["https://big-nose.ru:9100/uwords-picture/apple.jpg"], default=None)

    class Config:
        from_attributes = True


class UserWordDumpSchema(BaseModel):
    id: int = Field(examples=[1])
    word: WordDumpSchema
    user_id: str = Field(examples=["ijembbp53kbtSJ7FW3k68XQwJYp1"])
    frequency: int = Field(examples=[7])
    progress: int = Field(examples=[2])

    class Config:
        from_attributes = True
