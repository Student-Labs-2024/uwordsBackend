# В вашем файле main.py или где-то еще, где вы определяете ваше приложение FastAPI

import asyncio
from fastapi import FastAPI
from fastapi import WebSocket

app = FastAPI()

active_websockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    finally:
        active_websockets.remove(websocket)

# В вашем файле tasks.py или где-то еще, где вы определяете ваши задачи Celery

from celery.signals import task_failure

@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    for websocket in active_websockets:
        asyncio.create_task(websocket.send_text(f"Task {task_id} failed: {exception}"))



async def connect(self):
       # какой-то код
       self.process_task = asyncio.create_task(self.process_buffer())

async def process_buffer(self):
        while True:
            ### код проверки сообщения

            self.send("ОШИБКА")

            await asyncio.sleep(1)
