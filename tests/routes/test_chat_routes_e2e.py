# tests/routes/test_chat_routes_e2e.py
from fastapi.testclient import TestClient
import pytest
from backend.main import app
from unittest.mock import MagicMock
from backend.database.db_manager import get_db

client = TestClient(app)

def get_db_override():
    """테스트 중에는 이 함수가 get_db 대신 사용됩니다."""
    # 실제 DB에 연결하는 대신, 가짜 DB 세션을 반환합니다.
    yield MagicMock()

app.dependency_overrides[get_db] = get_db_override

@pytest.mark.skip(reason="아직 구현 중")
def test_chat_e2e_scenario_without_agent_mock(mocker):
    """
    Agent를 Mocking하지 않고, Agent의 하위 의존성(DB, LLM)만 Mocking하여
    Routes -> Agent 계층까지의 실제 통합을 테스트합니다.
    """
    # 준비 (Arrange)
    # 1. DB 계층 Mocking (아직 db_manager가 없으므로 Agent 내부의 uuid 호출을 Mocking)
    mocker.patch('backend.agents.chat_agent.uuid.uuid4', return_value='real-e2e-session-id')
    # (나중에 여기에 fetch_history, save_history 등을 mocking하는 코드가 들어갑니다)

    # 2. Core 계층 (LLM 호출) Mocking
    # Agent가 내부적으로 호출하는 _llm_reply를 Mocking합니다.
    mock_llm_reply = mocker.patch(
        'backend.agents.chat_agent.ChatAgent._llm_reply',
        return_value="실제 Agent가 호출한 LLM의 가짜 응답"
    )

    # --- 시나리오 1: 첫 번째 대화 ---
    first_request = { "user_id": "e2e_user", "model": "gpt-4o-mini", "message": "첫 메시지"}
    
    # 실행 (Act)
    # TestClient는 실제 FastAPI 앱을 실행하여 /api/chat 라우트를 호출하고,
    # 라우트는 실제 ChatAgent 인스턴스의 handle 메소드를 호출합니다.
    response = client.post("/api/chat", json=first_request)

    # 단언 (Assert)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["reply"] == "실제 Agent가 호출한 LLM의 가짜 응답"
    # 실제 Agent의 세션 생성 로직이 잘 동작했는지 확인
    assert response_data["session_id"] == "real-e2e-session-id"

    # Agent가 _llm_reply를 올바른 인자들로 호출했는지 검증
    mock_llm_reply.assert_called_once()