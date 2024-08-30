from typing import Tuple
from yoomoney import Client, Quickpay
from uuid import uuid4

from src.database.models import Bill
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

    async def check_payment(self, token: str, label_id: str) -> int:
        client = Client(token)
        history = client.operation_history(label=label_id)
        bill: Bill = await self.repo.get_one({Bill.label == label_id})
        try:
            operation = history.operations[0]
            if operation.status == "success" and not bill.success:
                await self.repo.update_one({Bill.id == bill.id}, {"success": True})
                return bill.sub_type
        except:
            return 0
        return 0

    async def get_bill(self, pay_id):
        return await self.repo.get_one({Bill.label == pay_id})

    async def get_all_bills(self):
        return await self.repo.get_all_by_filter()
