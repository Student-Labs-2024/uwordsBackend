from pydantic import BaseModel, Field
from typing import List, Optional


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
    pictureLink: str

    class ConfigDict:
        from_attributes = True


class TopicWords(BaseModel):
    title: str
    subtopics: List[SubtopicWords]

    class ConfigDict:
        from_attributes = True
