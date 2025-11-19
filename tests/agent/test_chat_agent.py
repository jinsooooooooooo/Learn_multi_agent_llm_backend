# tests/agents/test_chat_agent.py
import pytest
from unittest.mock import patch
from backend.agents.chat_agent import ChatAgent

@pytest.fixture
def chat_agent():
    """테스트를 위한 ChatAgent 인스턴스를 생성하는 Fixture"""
    return ChatAgent()

def test_handle_new_session(chat_agent, mocker):
    """
    첫 대화일 때 (session_id=None), 새로운 session_id를 생성하고
    올바른 파라미터로 _llm_reply를 호출하는지 테스트합니다.
    """
    # 준비 (Arrange)
    # _llm_reply 메소드를 Mocking하여 실제 LLM 호출을 방지합니다.
    mock_llm_reply = mocker.patch(
        'backend.agents.chat_agent.ChatAgent._llm_reply',
        return_value="LLM의 가짜 응답"
    )

    # DB 연동 부분을 가정하기 위한 가짜 uuid 생성 mock
    # uuid.uuid4()가 항상 예측 가능한 값을 반환하도록 설정
    mocker.patch('backend.agents.chat_agent.uuid.uuid4', return_value='new-mock-uuid')

    # 실행 (Act)
    reply, session_id = chat_agent.handle(
        session_id=None,
        user_id="test_user",
        model="gpt-4o-mini",
        message="안녕하세요"
    )

    # 단언 (Assert)
    assert reply == "LLM의 가짜 응답"
    assert session_id == 'new-mock-uuid'

    # _llm_reply가 올바른 인자들로 호출되었는지 확인
    # 이 테스트에서는 chat_history가 비어있을 것으로 예상
    mock_llm_reply.assert_called_once_with("gpt-4o-mini", "안녕하세요", [])

def test_handle_existing_session(chat_agent, mocker):
    """
    기존 대화일 때 (session_id 있음), _llm_reply를 올바르게 호출하는지 테스트
    (DB 연동이 구현되었다고 가정)
    """
    # 준비 (Arrange)
    # 이 테스트에서는 DB에서 이전 대화 기록을 가져왔다고 가정합니다.
    # 따라서 chat_history에 가짜 데이터를 넣습니다.
    # (실제로는 fetch_chat_history 함수를 mocking해야 합니다)
    
    mock_llm_reply = mocker.patch(
        'backend.agents.chat_agent.ChatAgent._llm_reply',
        return_value="LLM의 두 번째 가짜 응답"
    )

    # 실행 (Act)
    reply, session_id = chat_agent.handle(
        session_id="existing-session-123",
        user_id="test_user",
        model="gpt-4o-mini",
        message="제 이름이 뭔가요?"
    )

    # 단언 (Assert)
    assert reply == "LLM의 두 번째 가짜 응답"
    assert session_id == "existing-session-123" # 기존 세션 ID가 유지되는지 확인
    
    # 여기서 chat_history는 아직 DB 연동 전이라 빈 리스트[]로 넘어가는 것이 맞습니다.
    # 만약 DB 연동 후라면, fetch_history를 mocking하고 가짜 이력을 반환하게 한 뒤,
    # 그 가짜 이력이 _llm_reply에 잘 전달되는지 검증해야 합니다.
    mock_llm_reply.assert_called_once_with("gpt-4o-mini", "제 이름이 뭔가요?", [])