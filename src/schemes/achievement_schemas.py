from typing import Optional
from pydantic import BaseModel, Field


class AchievementCreate(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Полиглот!"])
    description: str = Field(examples=["Стандартное описание достижения."])
    category: str = Field(examples=["Слова"])
    stage: int = Field(examples=[1])
    target: int = Field(examples=[100])


class AchievementDump(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Complete 10 lessons"])
    description: str = Field(examples=["Complete 10 lessons to earn this achievement"])
    pictureLink: Optional[str] = Field(
        examples=["https://example.com/achievement.png"], default=None
    )
    category: str = Field(examples=["Learning"])
    stage: int = Field(examples=[1])
    target: int = Field(examples=[10])

    class Config:
        from_attributes = True


class AchievementUpdate(BaseModel):
    title: str = Field(examples=["Complete 10 lessons"])
    description: str = Field(examples=["Complete 10 lessons to earn this achievement"])
    pictureLink: Optional[str] = Field(
        examples=["https://example.com/achievement.png"], default=None
    )
    category: str = Field(examples=["Learning"])
    stage: int = Field(examples=[1])
    target: int = Field(examples=[10])


class UserAchievementDump(BaseModel):
    id: int = Field(examples=[1])
    user_id: int = Field(examples=[1])
    progress: int = Field(examples=[50])
    progress_percent: float = Field(examples=[50.0])
    is_completed: bool = Field(examples=[False])
    achievement: AchievementDump

    class Config:
        from_attributes = True
