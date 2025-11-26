from typing import Optional
from fastapi import APIRouter, Request
from backend.agents.naver_news_agent import NaverNewsAgent
from pydantic import BaseModel

router = APIRouter(tags=["Agent API"])
agent = NaverNewsAgent()

class NaverNewsRequest(BaseModel):
    chat_id: Optional[str] = None
    user_id: str
    model: str
    keywords: list[str]
    message: Optional[str] = "검색 뉴스 요약 해줘"


@router.post("/naver_news")
async def naver_news(payload: NaverNewsRequest):
    # data = await request.json()
    # user_input = data.get("message", "")
    response_articles, respnose_text, chat_id = agent.handle(payload)
    return {
        "agent": agent.name, 
        "articles": response_articles, 
        "reply": respnose_text,
        "chat_id" : chat_id
        }
