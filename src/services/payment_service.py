from yoomoney import Client, Quickpay
from uuid import uuid4


class PaymentService:
    @staticmethod
    async def create_payment_form(amount: int, receiver_id: str):
        label_id = str(uuid4().int)
        quick_pay = Quickpay(
            receiver=receiver_id,
            quickpay_form="shop",
            targets="Subscription",
            paymentType="SB",
            sum=amount,
            label=label_id,
        )
        return quick_pay.redirected_url, label_id

    @staticmethod
    async def check_payment(token: str, label_id, amount):
        client = Client(token)
        history = client.operation_history(label=label_id)
        try:
            operation = history[0]
            if operation.amount >= amount and operation.status == "success":
                return True
        except:
            return False