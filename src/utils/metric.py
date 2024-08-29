import aiohttp
from urllib.parse import urlencode

from src.config.instance import METRIC_TOKEN
from src.schemes.user_schemas import UserMetric
from src.utils.logger import metric_utils_logger


async def send_user_data(data: dict, server_url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url=server_url,
                headers={"Authorization": f"Bearer {METRIC_TOKEN}"},
                json=data,
            ) as response:
                if response.status == 200:
                    metric_utils_logger.info(f"Successfully sent data to server")
                else:
                    response_text = await response.text()
                    metric_utils_logger.error(
                        f"Failed to send data to server. Status code: {response.status}. Response: {response_text}"
                    )
        except aiohttp.ClientError as e:
            metric_utils_logger.error(f"Request exception occurred: {e}")


async def get_user_data(uwords_uid: str, server_url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        try:
            query = urlencode(
                {"uwords_uid": uwords_uid, "is_union": True, "metric_range": "alltime"}
            )
            async with session.get(
                url=f"{server_url}?{query}",
                headers={"Authorization": f"Bearer {METRIC_TOKEN}"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    metric_utils_logger.info(
                        f"Successfully retrieved additional user data: {data}"
                    )
                    return data
                else:
                    response_text = await response.text()
                    metric_utils_logger.error(
                        f"Failed to retrieve additional user data. Status code: {response.status}. Response: {response_text}"
                    )
                    return None
        except aiohttp.ClientError as e:
            metric_utils_logger.error(f"Request exception occurred: {e}")
            return None


async def get_user_metric(
    user_id: int, user_days: int, uwords_uid: str, server_url: str
):
    user_metric = await get_user_data(uwords_uid=uwords_uid, server_url=server_url)

    if user_metric:
        return UserMetric(
            user_id=user_id,
            days=user_days,
            alltime_userwords_amount=user_metric.get("alltime_userwords_amount"),
            alltime_learned_amount=user_metric.get("alltime_learned_amount"),
            alltime_learned_percents=user_metric.get("alltime_learned_percents"),
            alltime_speech_seconds=user_metric.get("alltime_speech_seconds"),
            alltime_video_seconds=user_metric.get("alltime_video_seconds"),
        )

    return UserMetric(
        user_id=user_id,
        days=user_days,
        alltime_userwords_amount=0,
        alltime_learned_amount=0,
        alltime_learned_percents=0,
        alltime_speech_seconds=0,
        alltime_video_seconds=0,
    )
