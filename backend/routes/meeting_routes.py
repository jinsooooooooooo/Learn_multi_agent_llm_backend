# backend/routes/meeting_routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Request
from backend.agents.meeting_agent import MeetingAgent
from pydantic import BaseModel
from backend.database.db_manager import get_db

router = APIRouter(tags=["Agent API"])
agent = MeetingAgent()

class MeetingRequest(BaseModel):
    """
    회의실 관련 AI 메세지 전송
    """
    chat_id: Optional[str] = None
    user_id: str = 'guest'
    model: str = 'gpt-4o-mini'
    message: str # 사용자의 입력 메시지 (필수 문자열 필드)



@router.post("/meeting")
async def meeting(payload: MeetingRequest, db = Depends(get_db)):
    # user_input = payload.message
    # response = agent.handle(user_input)
    response_text, chat_id = agent.handle( db, payload.chat_id, payload.user_id , payload.model, payload.message )

    return {
        "agent": agent.name, 
        "reply": response_text,
        "chat_id": chat_id
        }
