import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger("[AUTH UTILS]")
logging.basicConfig(level=logging.INFO)


async def send_user_data(data: dict, server_url: str):
    try:
        response = requests.post(server_url, json=data)
        if response.status_code == 200:
            logger.info(f"Successfully sent data to server")
        else:
            logger.error(
                f"Failed to send data to server. Status code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception occurred: {e}")


async def get_user_data(user_id: int, server_url: str):
    try:
        query = urlencode(
            {"user_id": user_id, "is_union": True, "metric_range": "alltime"}
        )
        response = requests.get(f"{server_url}?{query}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully retrieved additional user data: {data}")
            return data
        else:
            logger.error(
                f"Failed to retrieve additional user data. Status code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception occurred: {e}")
        return None
