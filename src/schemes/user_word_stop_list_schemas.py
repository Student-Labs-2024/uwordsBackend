from pydantic import BaseModel


class UserWordStopListCreate(BaseModel):
    user_id: int
    word_id: int
