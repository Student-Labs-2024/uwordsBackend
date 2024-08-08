from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.database.models import Achievement, User
from src.schemes.achievement_schemas import (
    AchievementCreate,
    AchievementDump,
    AchievementUpdate,
)
from src.services.achievement_service import AchievementService
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils import auth as auth_utils
from src.config import fastapi_docs_config as doc_data

achievement_router_v1 = APIRouter(prefix="/api/achievement", tags=["Achievement"])


@achievement_router_v1.post(
    "/add",
    response_model=AchievementDump,
    name=doc_data.ACHIEVEMENT_ADD_TITLE,
    description=doc_data.ACHIEVEMENT_ADD_DESCRIPTION,
)
async def add_achievement(
    achievement_data: AchievementCreate,
    achivement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):
    if await achivement_service.get([Achievement.title == achievement_data.title]):
        raise HTTPException(
            detail="Achievement already exist", status_code=status.HTTP_400_BAD_REQUEST
        )
    return await achivement_service.add_one(achievement_data.model_dump())


@achievement_router_v1.get(
    "/get",
    name=doc_data.ACHIEVEMENT_GET_TITLE,
    description=doc_data.ACHIEVEMENT_GET_DESCRIPTION,
)
async def get_achievement(
    achievement_id: int,
    achievement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):
    res = await achievement_service.get([Achievement.id == achievement_id])
    if res:
        return res
    raise HTTPException(
        detail="Achievement do not exist", status_code=status.HTTP_400_BAD_REQUEST
    )


@achievement_router_v1.get(
    "/get_all",
    response_model=list[AchievementDump],
    name=doc_data.ACHIEVEMENT_GET_ALL_TITLE,
    description=doc_data.ACHIEVEMENT_GET_ALL_DESCRIPTION,
)
async def get_all_achievements(
    achievement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):
    return await achievement_service.get_all()


@achievement_router_v1.delete(
    "/delete",
    name=doc_data.ACHIEVEMENT_DELETE_TITLE,
    description=doc_data.ACHIEVEMENT_DELETE_DESCRIPTION,
)
async def delete_topic(
    achievement_id: int,
    achievement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):
    achievement = await achievement_service.get([Achievement.id == achievement_id])
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Achievement not found"},
        )
    await achievement_service.delete_one(achievement_id)
    return {"msg": "Achievement deleted successfully"}


@achievement_router_v1.post(
    "/update",
    response_model=AchievementDump,
    name=doc_data.ACHIEVEMENT_UPDATE_TITLE,
    description=doc_data.ACHIEVEMENT_UPDATE_DESCRIPTION,
)
async def update_achievement(
    achievement_id: int,
    achievement_data: AchievementUpdate,
    achievement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):
    achievement = await achievement_service.get([Achievement.id == achievement_id])
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Achievement not found"},
        )
    return await achievement_service.update_one(
        achievement_id, achievement_data.model_dump()
    )
