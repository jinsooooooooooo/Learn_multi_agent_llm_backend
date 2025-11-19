# backend\agent\base_agent.py
from abc import ABC, abstractmethod
from backend.core.llm_core import call_llm

class BaseAgent(ABC):
    """모든 에이전트의 공통 기반 클래스"""
    
    def __init__(self, name: str, role_prompt: str):
        self.name = name
        self.role_prompt = role_prompt

    @abstractmethod
    def handle(self, session_id, user_id, model, message) -> str:
        """각 에이전트별 요청 처리 로직"""
        print( 
            f'[_agent.py] >>>>>> handle( self, session_id:str , user_id: str, model:str , message: str)  \n' 
            f'  - sesseion_id: {session_id} \n'
            f'  - user_id: {user_id} \n'
            f'  - model: {model} \n'
            f'  - message: {message} \n'
        )
        pass

        
    def _llm_reply(self, model:str , message: str, chat_history: list[dict] = None , prompt: str = None) -> str:
        """
        LLM 호출 공통 공통 래퍼(wrapper) 함수.
        Arguments:
            - model(str): 모델
            - message(str): 사용자의 신규 메세지
            - chat_history(turple): Optional
        Returns:
            - str: 신규 메세지에 대한 llm 답변
        """
        # full_prompt = f"{self.role_prompt}\n\n사용자 요청:\n{content}"
        final_prompt = prompt or self.role_prompt
        return call_llm(
            model=model,
            prompt=final_prompt,
            message=message,
            chat_history=chat_history
            # temperature는 llm_core의 기본값을 사용하므로 명시하지 않아도 됩니다.
        )
    







