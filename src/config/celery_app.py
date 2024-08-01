import time
from celery import Celery
from celery.schedules import crontab

from src.config.instance import REDIS_URL


app = Celery(
    "youwords_fastapi",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.celery.tasks", "src.celery.scheduled_tasks"],
)

app.autodiscover_tasks()

app.conf.timezone = 'UTC'
app.conf.beat_schedule = {
    'reset-limits': {
        'task': "reset_limits",
        'schedule': 10,
        'options': {'queue': 'scheduler'},
    },
    
    'check-sub': {
        'task': "check_sub",
        'schedule': 1200,
        'options': {'queue': 'scheduler'},
    },
    
}

