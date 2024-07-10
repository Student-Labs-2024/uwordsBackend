import logging

from src.database.models import User
from src.utils.repository import AbstractRepository

logger = logging.getLogger("[SERVICES USER]")
logging.basicConfig(level=logging.INFO)


class UserService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            return await self.repo.get_one(
                filters=[User.id == user_id]
            )
        except Exception as e:
            logger.info(f'[GET USER by ID] Error: {e}')
            return None
        
    async def get_user_by_email_provider(self, email: str, provider: str) -> User:
        try:
            return await self.repo.get_one(
                filters=[User.email == email, User.provider == provider]
            )
        except Exception as e:
            logger.info(f'[GET USER by EMAIL] Error: {e}')
            return None
        
    async def get_user_by_email(self, email: str) -> User:
        try:
            return await self.repo.get_one(
                filters=[User.email == email]
            )
        except Exception as e:
            logger.info(f'[GET USER by EMAIL] Error: {e}')
            return None
        
    async def create_user(self, user_data: dict) -> User:
        try:
            return await self.repo.add_one(data=user_data)
        except Exception as e:
            logger.info(f'[CREATE USER] Error: {e}')
            return None
        
    async def update_user(self, user_id: int, user_data: dict):
        try:
            return await self.repo.update_one(
                filters=[User.id == user_id],
                values=user_data
            )
        except Exception as e:
            logger.info(f'[UPDATE USER] Error: {e}')
            return None
        
    async def ban_user(self, user_id: int):
        try:
            return await self.repo.update_one(
                filters=[User.id == user_id],
                values={
                    "is_active": False
                }
            )
        except Exception as e:
            logger.info(f'[BAN USER] Error: {e}')
            return None
        
    async def delete_user(self, user_id: int):
        try:
            return await self.repo.delete_one(
                filters=[User.id == user_id]
            )
        except Exception as e:
            logger.info(f'[DELETE USER] Error: {e}')
            return None