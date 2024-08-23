import asyncio
import pytest
from unittest.mock import ANY, AsyncMock, MagicMock

from sqlalchemy import desc
from src.database.models import UserAchievement
from src.services.achievement_service import AchievementService
from src.utils.repository import AbstractRepository

@pytest.fixture
def service():
    repo = MagicMock(spec=AbstractRepository)
    service = AchievementService(repo)
    return service

class TestAchievementService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("achievement, expected_result", [
        ({"title": "Test Achievement", "description": "Test description"}, {"id": 1, "title": "Test Achievement", "description": "Test description"}),
        ({"title": "Another Achievement", "description": "Another description"}, {"id": 2, "title": "Another Achievement", "description": "Another description"}),
    ])
    async def test_add_one(self, service, achievement, expected_result):
        service.repo.add_one.return_value = asyncio.Future()
        service.repo.add_one.return_value.set_result(expected_result)

        result = await service.add_one(achievement)

        assert result == expected_result
        service.repo.add_one.assert_called_once_with(data=achievement)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("title, expected_result", [
        ("Test Achievement", {"id": 1, "title": "Test Achievement", "description": "Test description"}),
        ("Another Achievement", {"id": 2, "title": "Another Achievement", "description": "Another description"}),
    ])
    async def test_get(self, service, title, expected_result):
        service.repo.get_one.return_value = asyncio.Future()
        service.repo.get_one.return_value.set_result(expected_result)

        result = await service.get(title)

        assert result == expected_result
        service.repo.get_one.assert_called_once_with(title)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("expected_result", [
        [{"id": 1, "title": "Test Achievement", "description": "Test description"}, {"id": 2, "title": "Another Achievement", "description": "Another description"}],
        [],
    ])
    async def test_get_all(self, service, expected_result):
        service.repo.get_all_by_filter.return_value = asyncio.Future()
        service.repo.get_all_by_filter.return_value.set_result(expected_result)

        result = await service.get_all()

        assert result == expected_result
        service.repo.get_all_by_filter.assert_called_once_with()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("achievement_id, update_data, expected_result", [
        (1, {"description": "Updated description"}, {"id": 1, "title": "Test Achievement", "description": "Updated description"}),
        (2, {"title": "Updated title"}, {"id": 2, "title": "Updated title", "description": "Another description"}),
    ])
    async def test_update_one(self, service, achievement_id, update_data, expected_result):
        service.repo.update_one.return_value = asyncio.Future()
        service.repo.update_one.return_value.set_result(expected_result)

        result = await service.update_one(achievement_id, update_data)

        assert result == expected_result
        service.repo.update_one.assert_called_once_with(filters=ANY, values=update_data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("achievement_id", [
        1,
        2,
    ])
    async def test_delete_one(self, service, achievement_id):
        service.repo.delete_one.return_value = asyncio.Future()
        service.repo.delete_one.return_value.set_result(None)

        await service.delete_one(achievement_id)

        service.repo.delete_one.assert_called_once_with(filters=ANY)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_id, expected_result", [
        (1, [{"id": 1, "user_id": 1, "achievement_id": 1}, {"id": 2, "user_id": 1, "achievement_id": 2}]),
        (2, []),
    ])
    async def test_get_user_achievements(self, service, user_id, expected_result):
        service.repo.get_all_by_filter.return_value = asyncio.Future()
        service.repo.get_all_by_filter.return_value.set_result(expected_result)

        result = await service.get_user_achievements(user_id)

        assert result == expected_result




