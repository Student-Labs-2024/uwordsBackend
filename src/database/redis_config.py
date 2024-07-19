import redis

from src.config.instance import REDIS_HOST, REDIS_PORT, REDIS_PASS


redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
