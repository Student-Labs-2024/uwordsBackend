from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from src.database.models import User
from src.schemes.subscription_schemas import (
    SubscriptionDump,
    Subscription,
    SubscriptionUpdate,
)
from src.services.subscription_service import SubscriptionService
from src.utils.dependenes.sub_service_fabric import sub_service_fabric
from src.utils import auth as auth_utils
from src.config import fastapi_docs_config as doc_data

subscription_router_v1 = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@subscription_router_v1.post(
    "/add",
    response_model=SubscriptionDump,
    name=doc_data.SUB_ADD_TITLE,
    description=doc_data.SUB_ADD_DESCRIPTION,
)
async def add_new_type_of_sub(
    sub_data: Subscription,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    try:
        return await sub_service.add_sub(sub_data)
    except:
        raise HTTPException(
            detail="Subscription already exist", status_code=status.HTTP_400_BAD_REQUEST
        )


@subscription_router_v1.get(
    "/all",
    response_model=List[SubscriptionDump],
    name=doc_data.SUB_GET_ALL_TITLE,
    description=doc_data.SUB_GET_ALL_DESCRIPTION,
)
async def get_tariffs(
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_active_current_user),
):
    return await sub_service.get_tariffs(promo=user.promo)


@subscription_router_v1.get(
    "/get",
    response_model=SubscriptionDump,
    name=doc_data.SUB_GET_TITLE,
    description=doc_data.SUB_GET_DESCRIPTION,
)
async def get_sub(
    name: str,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    res = await sub_service.get_sub(name)
    if res:
        return res
    raise HTTPException(
        detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@subscription_router_v1.delete(
    "/delete",
    response_model=str,
    name=doc_data.SUB_DELETE_TITLE,
    description=doc_data.SUB_DELETE_DESCRIPTION,
)
async def delete_sub(
    name: str,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    if await sub_service.get_sub(name):
        await sub_service.delete_sub(name)
        return name
    raise HTTPException(
        detail="Subscription do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@subscription_router_v1.post(
    "/update",
    response_model=SubscriptionDump,
    name=doc_data.SUB_UPDATE_TITLE,
    description=doc_data.SUB_UPDATE_DESCRIPTION,
)
async def update_sub(
    name: str,
    sub_data: SubscriptionUpdate,
    sub_service: Annotated[SubscriptionService, Depends(sub_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    return await sub_service.update_sub(name, sub_data.model_dump())
