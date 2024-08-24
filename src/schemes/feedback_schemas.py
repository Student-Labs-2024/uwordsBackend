from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    stars: int = Field(examples=[5])
    message: str = Field(examples=["Отличное приложение!"])


class FeedbackDump(BaseModel):
    id: int = Field(examples=[1])
    user_id: int = Field(examples=[1])
    stars: int = Field(examples=[5])
    message: str = Field(examples=["Отличное приложение!"])
    created_at: datetime = Field(examples=["2024-07-18 10:30:45.999999"])

    class ConfigDict:
        from_attributes = True
