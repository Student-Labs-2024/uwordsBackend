from pydantic import BaseModel, Field


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
