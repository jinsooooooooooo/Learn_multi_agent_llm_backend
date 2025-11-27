# backend\agent\base_agent.py
from abc import ABC, abstractmethod
from backend.core.llm_core import call_llm, call_llm_stream
from backend.database.crud import chat_crud
from sqlalchemy.orm import Session


class BaseAgent(ABC):
    """모든 에이전트의 공통 기반 클래스"""
    
    def __init__(self, name: str, role_prompt: str):
        self.name = name
        self.role_prompt = role_prompt

    @abstractmethod
    def handle(self, db, chat_id, user_id, model, message) -> tuple[str,str]:
        """각 에이전트별 요청 처리 로직"""
        print(f'======'*20)
        print(f""" 
    - db: {db} 
    - sesseion_id: {chat_id} 
    - user_id: {user_id} 
    - model: {model} 
    - message: {message} 
        """)
        print(f'======'*20)
        pass


    def _create_chat_seesion(self, db:Session, user_id:str, agent_id:str) -> str:
        new_seesion = chat_crud.create_chat_session(db=db, user_id=user_id, agent_id=agent_id)
        return new_seesion.chat_id
    
    def _get_chat_history(self,db:Session, chat_id:str) -> list:
        chat_history = chat_crud.get_chat_history(db=db, chat_id=chat_id)
        return chat_history
    
    def _save_massgae_history(self,db:Session, chat_id:str, model_id: str, role:str, content:str, sequence:int) -> None:
        chat_crud.save_message(db=db, chat_id=chat_id, role=role, content=content, sequence=sequence,model_id=model_id)
        return None
    
    def _get_last_sequence(self,db:Session, chat_id:str) -> int:
        last_sequence = chat_crud.get_last_sequence(db=db, chat_id=chat_id)
        return last_sequence
    
    

        
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


