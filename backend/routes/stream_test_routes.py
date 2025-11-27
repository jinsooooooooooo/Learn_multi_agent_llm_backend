import json
from fastapi import APIRouter
router = APIRouter(tags=["RAG Management"])
from fastapi.responses import StreamingResponse



# ==========================================================
# [임시 디버깅용 코드] 아래 코드를 추가해주세요.
# ==========================================================

import asyncio
from typing import AsyncGenerator

async def test_stream() -> AsyncGenerator[str, None]:
    """
    Gemini API 없이, 1초마다 데이터를 전송하는 스트리밍 제너레이터입니다.
    이 함수가 클라이언트에 스트리밍되지 않으면 서버(Uvicorn) 문제이며,
    스트리밍되면 Gemini API와의 상호작용 문제일 가능성이 높습니다.
    """
    phrases = [
        "data: [테스트 1/5] 스트리밍 시작: 첫 번째 청크 전송\n\n",
        "data: [테스트 2/5] 1초 대기 후 두 번째 청크 전송\n\n",
        "data: [테스트 3/5] 2초 대기 후 세 번째 청크 전송\n\n",
        "data: [테스트 4/5] 2초 대기 후 네 번째 청크 전송\n\n",
        "data: [테스트 5/5] 스트리밍 완료: 마지막 청크 전송\n\n"
    ]
    
    delays = [0, 1, 2, 2, 1] # 각 청크 전송 전 대기 시간 (초)

    for i, phrase in enumerate(phrases):
        await asyncio.sleep(delays[i]) # 비동기적으로 대기 (논블로킹)
        print(f"[TEST PRINT] Yielding: {phrase.strip()}")
        reply = json.dumps(
            {
                "type": "text",
                "text": phrase    
            }
            , ensure_ascii=False
        )

        yield reply + "\n"

@router.post("/test/stream", summary="버퍼링 테스트용 스트림")
async def test_buffering():
    return StreamingResponse(
        test_stream(), # 새로 만든 테스트 제너레이터 사용
        media_type="text/event-stream"
    )
# ==========================================================
# [임시 디버깅용 코드] 여기까지 추가해주세요.
# ==========================================================
