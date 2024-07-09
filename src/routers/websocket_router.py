import asyncio
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.websockets import WebSocket

from src.schemes.schemas import ErrorCreate
from src.services.error_service import ErrorService
from src.services.user_word_service import UserWordService
from src.utils.dependenes.error_service_fabric import error_service_fabric
from src.utils.dependenes.user_word_fabric import user_word_service_fabric

websocket_router_v1 = APIRouter(prefix="/api/v1/websockets")
add_error_router = APIRouter(prefix="/api/v1/error")

@add_error_router.post("/add")
async def add_user_error(user_id, error_service: Annotated[ErrorService, Depends(error_service_fabric)],):
    try:
        error = ErrorCreate(
            user_id=user_id,
            message="test",
            description="test"
        )
        await error_service.add_one(error)
        return {"message": "Error added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@websocket_router_v1.websocket("/errors")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id,
    error_service: Annotated[ErrorService, Depends(error_service_fabric)],
):
    await websocket.accept()
    while True:
        # проверить бд на ошибки
        errors = await error_service.get_user_errors(user_id)
        for error in errors:
            if not error.is_send:
                await websocket.send_json(
                    data={
                        "msg": f"Отчет об ошибке: {error.message}, {error.description}"
                    }
                )

                await error_service.update_error_status(error_id=error.id)
        
        await asyncio.sleep(30)

