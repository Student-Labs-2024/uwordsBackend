import time
from celery import Celery

from .instance import CELERY_BROKER_URL


app = Celery(
    "youwords_fastapi", 
    broker=CELERY_BROKER_URL, 
    backend=CELERY_BROKER_URL,
    include=['src.celery.tasks']
)

app.autodiscover_tasks()


@app.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True
