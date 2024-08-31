from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta

from fastapi import APIRouter, Depends, HTTPException, status

from src.config.instance import WALLET_ID
from src.config import fastapi_docs_config as doc_data

from src.celery.tasks import auto_check_payment_task

from src.schemes.util_schemas import Bill
from src.database.models import User, Subscription

from src.services.user_service import UserService
from src.services.payment_service import PaymentService
from src.services.subscription_service import SubscriptionService

from src.utils import auth as auth_utils
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.payment_service_fabric import payment_service_fabric
from src.utils.exceptions import (
    BillNotFoundException,
    BillNotPaidException,
    SubscriptionNotFoundException,
)

payment_router_v1 = APIRouter(prefix="/api/payment", tags=["Payment"])


@payment_router_v1.get(
    "/form",
    response_model=tuple[str, str],
    name=doc_data.FORM_PAYMENT_TITLE,
    description=doc_data.FORM_PAYMENT_DESCRIPTION,
)
async def get_payment_form(
    sub_type: str,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    payment_service: Annotated[PaymentService, Depends(payment_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    sub: Subscription = await sub_service.get_sub(name=sub_type)
    if not sub:
        raise HTTPException(
            detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
        )

    price = sub.price

    if sub.promocode and user.promo:
        if sub.promocode == user.promo:
            price = sub.promo_price

    url, pay_id = await payment_service.create_payment_form(
        amount=price, receiver_id=WALLET_ID, sub_id=sub.id
    )

    auto_check_payment_task.apply_async(
        kwargs={"user_id": user.id, "pay_id": pay_id},
        countdown=1,
    )

    return url, pay_id


@payment_router_v1.get(
    "/check",
    response_model=bool,
    name=doc_data.CHECK_PAYMENT_TITLE,
    description=doc_data.CHECK_PAYMENT_DESCRIPTION,
)
async def check_payment_form(
    pay_id: str,
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    payment_service: Annotated[PaymentService, Depends(payment_service_fabric)],
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    if not await payment_service.check_payment(label_id=pay_id):
        raise BillNotPaidException()

    bill = await payment_service.get_bill(pay_id=pay_id)

    if not bill:
        raise BillNotFoundException()

    if bill.success:
        return True

    subscription = await sub_service.get_sub_by_id(id=bill.sub_type)

    if not subscription:
        raise SubscriptionNotFoundException()

    await payment_service.update_bill_success(bill_id=bill.id)

    now = datetime.now()
    expired_at = now + relativedelta(months=subscription.months)

    if subscription.free_period_days:
        expired_at += relativedelta(days=subscription.free_period_days)

    await user_service.update_user(
        user_id=user.id,
        user_data={
            "subscription_acquisition": now,
            "subscription_expired": expired_at,
            "subscription_type": bill.sub_type,
        },
    )

    return True


@payment_router_v1.get(
    "/bill/get",
    response_model=Bill,
    name=doc_data.BILL_GET_TITLE,
    description=doc_data.BILL_GET_DESCRIPTION,
)
async def get_bill(
    pay_id: str,
    payment_service: Annotated[PaymentService, Depends(payment_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    res = payment_service.get_bill(pay_id)
    if res:
        return res
    raise HTTPException(
        detail="Bill do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@payment_router_v1.get(
    "/bill/all",
    response_model=list[Bill],
    name=doc_data.BILL_ALL_TITLE,
    description=doc_data.BILL_ALL_DESCRIPTION,
)
async def get_all_bills(
    payment_service: Annotated[PaymentService, Depends(payment_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    return await payment_service.get_all_bills()
