# tests/core/test_llm_core.py
import pytest
from unittest.mock import MagicMock # Mock 객체 생성을 위해 import
from backend.core.llm_core import call_llm # 테스트할 함수를 import

# 1. OpenAI 모델 호출 테스트
def test_call_llm_with_openai_model(mocker):
    """
    OpenAI 모델(gpt-*)이 호출될 때, mocker를 사용하여
    실제 client.chat.completions.create API 호출을 가로채고(patch)
    미리 정의된 가짜 응답을 반환하도록 설정 응답 구조와 유사하게 만듭니다.
    mock_response = MagicMock()
    mock_response.choices[0.message.content = "이것은 OpenAI 가짜 응답입니다."
    """
    # 준비 (Arrange)
    # MagicMock으로 가짜 응답 객체를 만듭니다.
    mock_response = MagicMock()
    # 실제 OpenAI 응답 객체의 경로를 따라가며 속성을 설정합니다.
    # response.choices[0].message.content 형태를 흉내 냅니다.
    mock_response.choices[0].message.content = "이것은 OpenAI 가짜 응답입니다."

    # mocker.patch를 사용하여 실제 API 호출 경로를 가짜 객체로 대체합니다.
    mock_create = mocker.patch(
        'backend.core.llm_core.client.chat.completions.create', 
        return_value=mock_response # 이 함수가 호출되면 mock_response를 반환하도록 설정
    )

    # 실행 (Act)
    # 테스트할 함수를 실제 파라미터로 호출합니다.
    result = call_llm(
        model="gpt-4o-mini",
        prompt="테스트 프롬프트",
        message="테스트 메시지",
        chat_history=[]
    )

    # 단언 (Assert)
    # call_llm 함수의 반환 값이 우리가 설정한 가짜 응답과 일치하는지 확인합니다.
    assert result == "이것은 OpenAI 가짜 응답입니다."
    # 가짜 API 함수가 정확히 한 번 호출되었는지 확인합니다.
    mock_create.assert_called_once()


# 2. Gemini 모델 호출 테스트
def test_call_llm_with_gemini_model(mocker):
    """
    Gemini 모델이 호출될 때의 로직을 테스트합니다.
    이번에는 clientGemini...generate_content 경로를 가로챕니다.
    """
    # 준비 (Arrange)
    # Gemini 응답은 .text 속성을 가지므로, 더 간단한 Mock 객체를 만듭니다.
    mock_response = MagicMock()
    mock_response.text = "이것은 Gemini 가짜 응답입니다."
    
    mock_generate = mocker.patch(
        'backend.core.llm_core.clientGemini.models.generate_content',
        return_value=mock_response
    )

    # 실행 (Act)
    result = call_llm(
        model="gemini-1.5-flash",
        prompt="테스트 프롬프트",
        message="테스트 메시지",
        chat_history=[]
    )

    # 단언 (Assert)
    assert result == "이것은 Gemini 가짜 응답입니다."
    mock_generate.assert_called_once()

# 3. 비활성화 예시
@pytest.mark.skip(reason="이 테스트는 아직 준비되지 않았습니다.")
def test_future_feature():
    assert False