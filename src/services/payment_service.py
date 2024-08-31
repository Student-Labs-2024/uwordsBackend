from uuid import uuid4
from typing import Tuple
from yoomoney import Client, Quickpay, History, Operation

from src.database.models import Bill
from src.config.instance import PAYMENT_TOKEN
from src.utils.repository import AbstractRepository


class PaymentService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def create_payment_form(
        self, amount: int, receiver_id: str, sub_id: int
    ) -> Tuple[str, str]:
        label_id = str(uuid4().int)
        quick_pay = Quickpay(
            receiver=receiver_id,
            quickpay_form="shop",
            targets="Subscription",
            paymentType="SB",
            sum=amount,
            label=label_id,
        )
        await self.repo.add_one(
            {"label": label_id, "sub_type": sub_id, "amount": amount}
        )
        return quick_pay.redirected_url, label_id

    async def check_payment(self, label_id: str) -> bool:
        client = Client(token=PAYMENT_TOKEN)
        history: History = client.operation_history(label=label_id)

        if len(history.operations) != 0:
            operation: Operation = history.operations[0]

            if operation.status == "success":
                return True

        return False

    async def get_bill(self, pay_id) -> Bill:
        return await self.repo.get_one({Bill.label == pay_id})

    async def update_bill_success(self, bill_id: int) -> Bill:
        return await self.repo.update_one(
            filters=[Bill.id == bill_id], values={"success": True}
        )

    async def get_all_bills(self):
        return await self.repo.get_all_by_filter()
