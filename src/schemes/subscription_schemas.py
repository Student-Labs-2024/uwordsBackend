from typing import Optional

from pydantic import BaseModel, Field


class Subscription(BaseModel):
    name: str = Field(examples=["Premium"])
    price: int = Field(examples=[1990])
    price_str: str = Field(examples=["1990,00 ₽ в год"])
    months: int = Field(examples=[12])
    old_price: Optional[int] = Field(examples=[3588], default=None)
    old_price_str: Optional[str] = Field(examples=["3588,00 ₽ в год"], default=None)
    free_period_days: Optional[int] = Field(examples=[7], default=None)
    free_period_str: Optional[str] = Field(
        examples=["1 неделя бесплатно"], default=None
    )
    promocode: Optional[str] = Field(examples=["promo123"], default=None)
    promo_price: Optional[int] = Field(examples=[499], default=None)
    promo_price_str: Optional[str] = Field(
        examples=["После 499,00 ₽ каждый год"], default=None
    )
    comment: Optional[str] = Field(examples=["После 1990,00 ₽ каждый год"])
    discount: Optional[int] = Field(examples=[80], default=None)


class SubscriptionUpdate(BaseModel):
    price: int = Field(examples=[1990])
    price_str: str = Field(examples=["1990,00 ₽ в год"])
    months: int = Field(examples=[12])
    old_price: Optional[int] = Field(examples=[3588], default=None)
    old_price_str: Optional[str] = Field(examples=["3588,00 ₽ в год"], default=None)
    free_period_days: Optional[int] = Field(examples=[7], default=None)
    free_period_str: Optional[str] = Field(
        examples=["1 неделя бесплатно"], default=None
    )
    promocode: Optional[str] = Field(examples=["promo123"], default=None)
    promo_price: Optional[int] = Field(examples=[499], default=None)
    promo_price_str: Optional[str] = Field(
        examples=["После 499,00 ₽ каждый год"], default=None
    )
    comment: Optional[str] = Field(examples=["После 1990,00 ₽ каждый год"])
    discount: Optional[int] = Field(examples=[80], default=None)


class SubscriptionDump(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Premium"])
    price: int = Field(examples=[1990])
    price_str: str = Field(examples=["1990,00 ₽ в год"])
    months: int = Field(examples=[12])
    old_price: Optional[int] = Field(examples=[3588], default=None)
    old_price_str: Optional[str] = Field(examples=["3588,00 ₽ в год"], default=None)
    free_period_days: Optional[int] = Field(examples=[7], default=None)
    free_period_str: Optional[str] = Field(
        examples=["1 неделя бесплатно"], default=None
    )
    comment: Optional[str] = Field(examples=["После 1990,00 ₽ каждый год"])
    discount: Optional[int] = Field(examples=[80], default=None)


class SubscriptionDumpAllData(BaseModel):
    id: int = Field(examples=[1])
    name: str = Field(examples=["Premium"])
    price: int = Field(examples=[1990])
    price_str: str = Field(examples=["1990,00 ₽ в год"])
    months: int = Field(examples=[12])
    old_price: Optional[int] = Field(examples=[3588], default=None)
    old_price_str: Optional[str] = Field(examples=["3588,00 ₽ в год"], default=None)
    free_period_days: Optional[int] = Field(examples=[7], default=None)
    free_period_str: Optional[str] = Field(
        examples=["1 неделя бесплатно"], default=None
    )
    promocode: Optional[str] = Field(examples=["promo123"], default=None)
    promo_price: Optional[int] = Field(examples=[499], default=None)
    promo_price_str: Optional[str] = Field(
        examples=["После 499,00 ₽ каждый год"], default=None
    )
    comment: Optional[str] = Field(examples=["После 1990,00 ₽ каждый год"])
    discount: Optional[int] = Field(examples=[80], default=None)
