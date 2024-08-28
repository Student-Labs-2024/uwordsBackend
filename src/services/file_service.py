import logging
from src.utils.repository import AbstractRepository
from src.utils.logger import file_service_logger


class FileService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_file(self, path, data):
        await self.repo.add_one(data, path)

    async def delete_file(self, path):
        await self.repo.delete_one(path)
