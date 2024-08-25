from typing import List, Optional
from src.database import models
from src.schemes.subscription_schemas import Subscription, SubscriptionDump
from src.utils.repository import AbstractRepository


class SubscriptionService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_sub(self, sub: Subscription):
        return await self.repo.add_one(data=sub.model_dump())

    async def get_sub_by_promo(self, promo: str) -> models.Subscription:
        return await self.repo.get_one(filters=[models.Subscription.promocode == promo])

    async def get_all(self) -> List[models.Subscription]:
        return await self.repo.get_all_by_filter(
            filters=[models.Subscription.is_active == True]
        )

    async def get_tariffs(self, promo: Optional[str] = None) -> List[SubscriptionDump]:
        tariffs = await self.get_all()

        output = []

        for tariff in tariffs:
            price = tariff.price
            price_str = tariff.price_str
            old_price = tariff.old_price
            old_price_str = tariff.old_price_str
            comment = tariff.comment

            if tariff.promocode and promo:
                if tariff.promocode == promo:
                    price = tariff.promo_price
                    price_str = tariff.promo_price_str
                    old_price = tariff.price
                    old_price_str = tariff.price_str
                    comment = f"Промокод применён! Для вас действует специальная цена"

            output.append(
                SubscriptionDump(
                    id=tariff.id,
                    name=tariff.name,
                    price=price,
                    price_str=price_str,
                    old_price=old_price,
                    months=tariff.months,
                    old_price_str=old_price_str,
                    free_period_days=tariff.free_period_days,
                    free_period_str=tariff.free_period_str,
                    comment=comment,
                    discount=tariff.discount,
                )
            )

        return output

    async def get_sub(self, name: str):
        return await self.repo.get_one([models.Subscription.name == name])

    async def get_sub_by_id(self, id: int) -> Subscription:
        return await self.repo.get_one([models.Subscription.id == id])

    async def update_sub(self, name: str, data):
        return await self.repo.update_one([models.Subscription.name == name], data)

    async def delete_sub(self, name: str):
        await self.repo.delete_one([models.Subscription.name == name])
