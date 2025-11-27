# rag_routes.py

from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# 1. RAG DB 세션을 가져오는 의존성 함수를 import 합니다.
from backend.database.db_manager import get_db
# 2. 우리가 만든 핵심 처리 함수를 import 합니다.
from backend.core.rag_engine import refresh_rag_data

from pydantic import BaseModel

from backend.agents.rag_chat_agent import RagChatAgent

# 3. RAG 관리용 API 라우터를 생성합니다.
router = APIRouter(tags=["RAG Management"])

agent = RagChatAgent()


class RagChatRequest(BaseModel):
    """
    RAG 채팅 Agent 요청 
    """
    # agent_id: str = "ChatAgent"
    chat_id: Optional[str] = None
    user_id: str = 'guest'
    model: str = 'gpt-4o-mini'
    message: str # 사용자의 입력 메시지 (필수 문자열 필드)




@router.post("/rag/chat/stream", summary="RAG 기반 채팅(Ncp object Storage 파일 참고")
async def rag_chat_stream( 
    payload: RagChatRequest,
    db: Session = Depends(get_db),
):
    # StreamingResponse에 에이전트의 비동기 제너레이터 함수를 그대로 전달합니다.
    return StreamingResponse(
        agent._handle_stream(
            db=db,
            chat_id=payload.chat_id,
            user_id=payload.user_id,
            model=payload.model,
            message=payload.message
        ),
        media_type="text/event-stream"
    )



             
@router.post("/rag/chat", summary="RAG 기반 채팅(Ncp object Storage 파일 참고))")
async def rag_chat( 
    payload: RagChatRequest,
    db: Session = Depends(get_db),
):
    
    response_text, seesion_id = agent.handle(
        db=db,
        # rag_db=rag_db,
        chat_id=payload.chat_id,
        user_id=payload.user_id,
        model=payload.model,
        message=payload.message
        )
        
    return {
            "agent": agent.name,
            "reply": response_text, 
            "chat_id": seesion_id}




@router.post("/rag/refresh", summary="RAG 데이터 동기 처리") # OpenAPI 문서에 표시될 요약 추가
async def refresh_rag_sync(
    db: Session = Depends(get_db)
):
    """
    (동기 방식) NCP Object Storage와 RAG DB를 동기화합니다.
    모든 작업이 완료될 때까지 클라이언트 연결을 유지합니다. (Timeout 주의)
    """
    # 4. 핵심 로직:
    refresh_rag_data(db=db)

    # 5. 클라이언트에게 작업이 시작되었음을 알리는 응답을 즉시 보냅니다.
    return {"message": "RAG data refresh process done"}

@router.post("/rag/refresh_bg",  summary="RAG 데이터 비동기 처리")
async def refresh_rag_background(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    NCP Object Storage의 문서들을 RAG DB와 동기화하는
    백그라운드 작업을 트리거합니다.

    클라이언트에게는 즉시 응답을 반환하고, 실제 데이터 처리 작업은
    서버 백그라운드에서 실행됩니다.
    """
    # 4. 핵심 로직:
    # background_tasks.add_task()에 실행할 함수와 그 함수에 전달할 인자들을 넘겨줍니다.
    # FastAPI는 이 요청에 대한 응답을 보낸 "후에" refresh_rag_data(db=db)를 실행합니다.
    background_tasks.add_task(refresh_rag_data, db)

    # 5. 클라이언트에게 작업이 시작되었음을 알리는 응답을 즉시 보냅니다.
    return {"message": "RAG data refresh process has been started in the background."}



