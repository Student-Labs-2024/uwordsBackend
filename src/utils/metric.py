import aiohttp
import logging
from urllib.parse import urlencode

logger = logging.getLogger("[METRIC UTILS]")
logging.basicConfig(level=logging.INFO)


async def send_user_data(data: dict, server_url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(server_url, json=data) as response:
                if response.status == 200:
                    logger.info(f"Successfully sent data to server")
                else:
                    response_text = await response.text()
                    logger.error(
                        f"Failed to send data to server. Status code: {response.status}. Response: {response_text}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Request exception occurred: {e}")


async def get_user_data(user_id: int, server_url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        try:
            query = urlencode(
                {"user_id": user_id, "is_union": True, "metric_range": "alltime"}
            )
            async with session.get(f"{server_url}?{query}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved additional user data: {data}")
                    return data
                else:
                    response_text = await response.text()
                    logger.error(
                        f"Failed to retrieve additional user data. Status code: {response.status}. Response: {response_text}"
                    )
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Request exception occurred: {e}")
            return None
