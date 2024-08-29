from io import BytesIO
from typing import Annotated, List
from fastapi import APIRouter, Depends, File, UploadFile

from src.config.instance import MINIO_BUCKET_ACHIEVEMENT_ICONS, MINIO_HOST
from src.database.models import Achievement, User
from src.schemes.achievement_schemas import (
    AchievementCreate,
    AchievementDump,
    AchievementUpdate,
)

from src.services.minio_uploader import MinioUploader
from src.services.services_config import mc
from src.services.user_service import UserService
from src.services.achievement_service import AchievementService
from src.services.user_achievement_service import UserAchievementService

from src.utils import auth as auth_utils
from src.utils import helpers as helper_utils
from src.utils.exceptions import (
    AchievementAlreadyExistsException,
    AchievementNotFoundException,
    AchievementDoesNotExistException,
)
from src.utils.logger import achievement_router_logger
from src.utils.dependenes.user_service_fabric import user_service_fabric
from src.utils.dependenes.achievement_service_fabric import achievement_service_fabric
from src.utils.dependenes.user_achievement_fabric import user_achievement_service_fabric

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
    user_achivement_service: Annotated[
        UserAchievementService, Depends(user_achievement_service_fabric)
    ],
    user_service: Annotated[UserService, Depends(user_service_fabric)],
    user: User = Depends(auth_utils.get_admin_user),
):
    if await achivement_service.get([Achievement.title == achievement_data.title]):
        raise AchievementAlreadyExistsException()

    achievement = await achivement_service.add_one(achievement_data.model_dump())
    users = await user_service.get_users()

    achievements = await achivement_service.get_all()

    await user_achivement_service.update_user_achievements(
        users=users, achievements=achievements
    )

    return achievement


@achievement_router_v1.post(
    "/icon",
    response_model=AchievementDump,
    name=doc_data.ACHIEVEMENT_ICON_TITLE,
    description=doc_data.ACHIEVEMENT_ICON_DESCRIPTION,
)
async def upload_subtopic_icon(
    achievement_id: int,
    achievement_icon: Annotated[
        UploadFile, File(description="A file read as UploadFile")
    ],
    achievement_service: Annotated[
        AchievementService, Depends(achievement_service_fabric)
    ],
    user: User = Depends(auth_utils.get_admin_user),
):

    achievement = await achievement_service.get([Achievement.id == achievement_id])

    if not achievement:
        raise AchievementNotFoundException()

    mimetype = await helper_utils.check_mime_type_icon(
        filename=achievement_icon.filename
    )

    filename: str = achievement.title

    object_name = f"{filename.replace(' ', '_')}.svg"

    filedata = await achievement_icon.read()

    bytes_file = BytesIO(filedata)
    bytes_file.seek(0)

    found_subtopic_icon_bucket = mc.bucket_exists(MINIO_BUCKET_ACHIEVEMENT_ICONS)
    if not found_subtopic_icon_bucket:
        await MinioUploader.create_bucket(MINIO_BUCKET_ACHIEVEMENT_ICONS)

    await MinioUploader.upload_object(
        bucket_name=MINIO_BUCKET_ACHIEVEMENT_ICONS,
        object_name=object_name,
        data=bytes_file,
        lenght=bytes_file.getbuffer().nbytes,
        type=mimetype,
    )

    picture_link = f"{MINIO_HOST}/{MINIO_BUCKET_ACHIEVEMENT_ICONS}/{object_name}"

    return await achievement_service.update_one(
        achievement_id=achievement_id, update_data={"pictureLink": picture_link}
    )


@achievement_router_v1.get(
    "/get",
    response_model=AchievementDump,
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
    raise AchievementDoesNotExistException()


@achievement_router_v1.get(
    "/get_all",
    response_model=List[AchievementDump],
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
        raise AchievementNotFoundException()
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
        raise AchievementNotFoundException()
    return await achievement_service.update_one(
        achievement_id, achievement_data.model_dump()
    )
