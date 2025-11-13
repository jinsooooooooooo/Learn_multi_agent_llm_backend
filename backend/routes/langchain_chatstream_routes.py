# backend\routes\langchain_chatstream_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from agents.langchain_chatstream_agent import LangchainChatStreamAgent

router = APIRouter(tags=["LangChain Chat"])

@router.post("/langchain/chatstream")
async def chat_with_stream(request: Request):
    """
    LangChain 기반 Streaming Chat API
    """
    data = await request.json()
    user_id = data.get("user_id", "guest")
    message = data.get("message", "")

    agent = LangchainChatStreamAgent(user_id=user_id)
    stream = agent.handle_stream(message)

    return StreamingResponse(stream, media_type="text/event-stream")
