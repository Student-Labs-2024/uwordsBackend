from src.schemes.schemas import ErrorCreate, ErrorDump
from src.utils.repository import AbstractRepository
from src.database.models import Error


class ErrorService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, error: ErrorCreate):
        await self.repo.add_one(dict(error))

    async def get_all(self):
        return await self.repo.get_all_by_filter()
    
    async def get_user_errors(self, user_id: str) -> list[ErrorDump]: 
        return await self.repo.get_all_by_filter([Error.user_id == user_id], Error.id.desc())
    
    async def update_error_status(self, error_id: int):
        return await self.repo.update_one(
            filters=[Error.id == error_id], 
            values={"is_send": True}
        )
