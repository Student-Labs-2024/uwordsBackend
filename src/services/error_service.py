from src.database.models import Error
from src.schemes.error_schemas import ErrorCreate, ErrorDump

from src.utils.repository import AbstractRepository


class ErrorService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, error: ErrorCreate) -> Error:
        await self.repo.add_one(dict(error))

    async def get_all(self) -> list[Error]:
        return await self.repo.get_all_by_filter()

    async def get_user_errors(self, user_id: int) -> list[ErrorDump]:
        return await self.repo.get_all_by_filter(
            [Error.user_id == user_id], Error.id.desc()
        )

    async def update_error_status(self, error_id: int) -> Error:
        return await self.repo.update_one(
            filters=[Error.id == error_id], values={"is_send": True}
        )
