from typing import Optional

from pydantic import BaseModel, Field


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
