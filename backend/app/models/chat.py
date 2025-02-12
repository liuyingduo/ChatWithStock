from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class Message(BaseModel):
    role: str
    content: str
    data: Optional[Dict[str, Any]] = None

class ChatHistory(BaseModel):
    messages: List[Message] 