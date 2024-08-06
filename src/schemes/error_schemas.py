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
