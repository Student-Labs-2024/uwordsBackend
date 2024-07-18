from src.services.file_service import FileService
from src.utils.repository import LocalFileRepository


def file_service_fabric():
    return FileService(LocalFileRepository())
