import pytest
from unittest.mock import MagicMock, patch
from backend.agents.chat_agent import ChatAgent

@pytest.fixture
def chat_agent():
    """테스트를 위한 ChatAgent 인스턴스를 생성하는 Fixture"""
    return ChatAgent()

def test_handle_new_session(chat_agent, mocker):
    """(상황) 첫 대화일 때, (기대) 새로운 세션을 '생성'하고 LLM을 호출하는지 테스트"""
    # 준비 (Arrange)
    mock_db_session = MagicMock()
    mock_llm_reply = mocker.patch('backend.agents.chat_agent.ChatAgent._llm_reply', return_value="LLM의 가짜 응답")

    # chat_crud 의존성 Mocking
    mock_session = MagicMock()
    mock_session.chat_id = 'new-mock-uuid'
    mock_create_session = mocker.patch('backend.agents.chat_agent.chat_crud.create_chat_session', return_value=mock_session)
    mocker.patch('backend.agents.chat_agent.chat_crud.get_last_sequence', return_value=0)
    mock_save_message = mocker.patch('backend.agents.chat_agent.chat_crud.save_message')

    # 실행 (Act)
    reply, chat_id = chat_agent.handle(
        db=mock_db_session,
        chat_id=None,
        user_id="test_user",
        model="gpt-4o-mini",
        message="안녕하세요"
    )

    # 단언 (Assert)
    assert reply == "LLM의 가짜 응답"
    assert chat_id == 'new-mock-uuid'
    
    # 올바른 함수들이 올바른 인자들로 호출되었는지 검증
    mock_create_session.assert_called_once_with(db=mock_db_session, user_id="test_user", agent_id="ChatAgent", model_id="gpt-4o-mini")
    mock_llm_reply.assert_called_once_with(model="gpt-4o-mini", message="안녕하세요", chat_history=[])
    assert mock_save_message.call_count == 2

def test_handle_existing_session(chat_agent, mocker):
    """(상황) 기존 대화일 때, (기대) 대화 기록을 '조회'하고 LLM을 호출하는지 테스트"""
    # 준비 (Arrange)
    mock_db_session = MagicMock()
    mock_llm_reply = mocker.patch('backend.agents.chat_agent.ChatAgent._llm_reply', return_value="LLM의 두 번째 가짜 응답")
    
    # chat_crud 의존성 Mocking
    mock_history_message = MagicMock()
    mock_history_message.role = "user"
    mock_history_message.content = "이전 질문"
    mock_get_history = mocker.patch('backend.agents.chat_agent.chat_crud.get_chat_history', return_value=[mock_history_message])

    mocker.patch('backend.agents.chat_agent.chat_crud.get_last_sequence', return_value=1)
    mocker.patch('backend.agents.chat_agent.chat_crud.save_message')

    # 실행 (Act)
    reply, chat_id = chat_agent.handle(
        db=mock_db_session,
        chat_id="existing-session-123",
        user_id="test_user",
        model="gpt-4o-mini",
        message="제 이름이 뭔가요?"
    )

    # 단언 (Assert)
    assert reply == "LLM의 두 번째 가짜 응답"
    assert chat_id == "existing-session-123"

    # 올바른 함수들이 올바른 인자들로 호출되었는지 검증
    mock_get_history.assert_called_once_with(db=mock_db_session, chat_id="existing-session-123")
    expected_history = [{"role": "user", "content": "이전 질문"}]
    mock_llm_reply.assert_called_once_with(model="gpt-4o-mini", message="제 이름이 뭔가요?", chat_history=expected_history)