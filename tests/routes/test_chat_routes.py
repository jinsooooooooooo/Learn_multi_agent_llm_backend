# tests/routes/test_chat_routes.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app # 테스트할 FastAPI 앱 객체를 import 합니다.

# TestClient 인스턴스를 생성합니다.
# 이 client 객체를 통해 가상의 API 요청을 보낼 수 있습니다.
client = TestClient(app)


def test_chat_first_message_success(mocker):
    """
    /api/chat 엔드포인트에 첫 번째 메시지를 보냈을 때 (session_id 없이),
    성공적으로 응답(200 OK)하고 새로운 session_id를 포함하는지 테스트합니다.
    """
    # 준비 (Arrange)
    # Agent의 handle 메소드가 실제 LLM을 호출하지 않도록 Mocking 합니다.
    # 이 테스트의 목적은 '라우트'가 '에이전트'를 잘 호출하고 응답을 잘 포장하는지 보는 것이지,
    # 에이전트의 내부 로직 전체를 테스트하는 것이 아닙니다.
    # agent.handle이 (응답 텍스트, 세션 ID) 튜플을 반환하도록 설정합니다.
    mocker.patch(
        'backend.routes.chat_routes.agent.handle',
        return_value=("안녕하세요, 첫 대화입니다.", "new-session-id-123")
    )

    # 테스트할 요청 본문 (첫 대화이므로 session_id가 없음)
    request_payload = {
        "user_id": "test_user",
        "model": "gpt-4o-mini",
        "message": "안녕하세요"
    }

    # 실행 (Act)
    # client.post를 사용하여 가상의 POST 요청을 보냅니다.
    response = client.post("/api/chat", json=request_payload)

    # 단언 (Assert)
    # 1. 응답 상태 코드가 200 OK 인지 확인합니다.
    assert response.status_code == 200
    
    # 2. 응답 본문(JSON)을 파싱합니다.
    response_data = response.json()
    
    # 3. 응답 본문의 내용이 우리가 예상한 값과 일치하는지 확인합니다.
    assert response_data["agent"] == "ChatAgent"
    assert response_data["reply"] == "안녕하세요, 첫 대화입니다."
    assert response_data["session_id"] == "new-session-id-123"
