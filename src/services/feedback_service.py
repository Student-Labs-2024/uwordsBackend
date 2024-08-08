from src.database.models import Feedback
from src.schemes.feedback_schemas import FeedbackCreate, FeedbackDump
from src.utils.repository import AbstractRepository


class FeedbackService:
    def __init__(self, repo: AbstractRepository):
        self.repo = repo

    async def add_one(self, user_id: int, feedback: FeedbackCreate) -> Feedback:
        feedback_data = feedback.model_dump()
        feedback_data["user_id"] = user_id
        return await self.repo.add_one(feedback_data)

    async def get_all(self) -> list[Feedback]:
        return await self.repo.get_all_by_filter()

    async def get_user_feedback(self, user_id: int) -> list[FeedbackDump]:
        return await self.repo.get_all_by_filter(
            [Feedback.user_id == user_id], Feedback.id.desc()
        )

    async def update_feedback(self, feedback_id: int, update_data: dict) -> Feedback:
        return await self.repo.update_one(
            filters=[Feedback.id == feedback_id], values=update_data
        )

    async def user_has_feedback(self, user_id: int) -> bool:
        feedbacks = await self.get_user_feedback(user_id)
        return len(feedbacks) > 0
