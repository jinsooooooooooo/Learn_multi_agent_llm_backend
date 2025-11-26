# backend/routes/chat_routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from backend.agents.chat_agent import ChatAgent
from backend.database.db_manager import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["Agent API"])
agent = ChatAgent()

# Pydantic 모델 정의 (요청 본문 Schema)
class ChatRequest(BaseModel):
    """
    llm Chat을 보내기이한 메세지 전송
    """
    # agent_id: str = "ChatAgent"
    chat_id: Optional[str] = None
    user_id: str = 'guest'
    model: str = 'gpt-4o-mini'
    message: str # 사용자의 입력 메시지 (필수 문자열 필드)

class ChatResponse(BaseModel):
    agent: str
    reply: str
    seesion_id: str    
    

@router.post("/chat")
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    # data = await request.json()
    # user_input = data.get("message", "")
    # user_input = data.message
    response_text, chat_id = agent.handle(  
        db=db,
        chat_id=data.chat_id, 
        user_id=data.user_id , 
        model=data.model, 
        message=data.message 
    )
    
    return {
            "agent": agent.name,
            "reply": response_text, 
            "chat_id":chat_id}
