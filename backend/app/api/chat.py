from fastapi import APIRouter, HTTPException
from ..models.chat import Message
from ..services.chat_service import ChatService
from typing import Dict, Any

router = APIRouter()
chat_service = None

def init_router(service: ChatService):
    global chat_service
    chat_service = service

@router.post("/")
async def chat(message: Message) -> Dict[str, Any]:
    try:
        if message.role != "user":
            raise HTTPException(status_code=400, detail="Invalid message role")
        
        response = await chat_service.process_message(message.content)
        return {
            "role": "assistant",
            "content": response["content"],
            "data": response.get("data")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 