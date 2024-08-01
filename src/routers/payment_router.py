from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.schemes.schemas import Bill
from src.utils import auth as auth_utils
from src.config.instance import WALLET_ID, PAYMENT_TOKEN
from src.database.models import User, Subscription
from src.services.payment_service import PaymentService
from src.services.subscription_service import SubscriptionService
from src.services.user_service import UserService
from src.utils.dependenes.payment_service_fabric import payment_service_fabric
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.config import fastapi_docs_config as doc_data

payment_router_v1 = APIRouter(prefix="/api/payment", tags=["Payment"])


@payment_router_v1.get(
    "/form",
    response_model=tuple[str, str],
    name=doc_data.FORM_PAYMENT_TITLE,
    description=doc_data.FORM_PAYMENT_DESCRIPTION,
)
async def get_payment_form(
    sub_type,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    payment_service: Annotated[PaymentService, Depends(payment_service_fabric)],
):
    sub: Subscription = await sub_service.get_sub(sub_type)
    if sub:
        url, pay_id = await payment_service.create_payment_form(
            sub.price, WALLET_ID, sub.id
        )
        return url, pay_id
    raise HTTPException(
        detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


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
    user: User = Depends(auth_utils.get_active_current_user),
):
    sub_id = await payment_service.check_payment(PAYMENT_TOKEN, str(pay_id))
    if sub_id:
        await user_service.update_user(
            user.id,
            {
                User.subscription_acquisition: datetime.now(),
                User.subscription_type: sub_id,
            },
        )
        return True
    return False


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
