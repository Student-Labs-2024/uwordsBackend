import time
from celery import Celery

from src.config.instance import REDIS_URL


app = Celery(
    "youwords_fastapi",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.celery.tasks"],
)

app.autodiscover_tasks()


@app.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True
