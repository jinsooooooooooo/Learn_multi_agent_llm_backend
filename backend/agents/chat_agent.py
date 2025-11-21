# backend/agnet/chat_agent.py
from sqlalchemy import func
from backend.agents.base_agent import BaseAgent
from sqlalchemy.orm import Session
import uuid

from backend.database.crud import chat_crud

class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ChatAgent",
            role_prompt=(
                "당신은 사용자의 일상 업무를 도와주는 AI 어시스턴트입니다. "
                "짧고 명확하게 대답하세요."
            ),
        )

    def handle(self, db: Session, session_id:str , user_id: str, model:str , message: str) -> tuple[str, str] :
        """일반 대화 처리"""
        
        chat_history = [] 

        # 1. if seesion_id 가 없으면: = 첫 대화 이므로 세션 아이디 생성
        #   databse에서 "chat_seesion" 테이블에 세션 데이터를 insert 하여 pk로 session_id(=uuid) 반환 받아 사용 한다. 
        if session_id is None or session_id.strip() == "":
            # print(f'[chat_agent.py] create new seesion_id!!! -> {session_id}')
            # session_id = str(uuid.uuid4()) # (임시조치)
            new_seesion = chat_crud.create_chat_session(
                db=db,
                user_id=user_id,
                agent_id=self.name,
                model_id=model
            )
            session_id = str(new_seesion.session_id)
        # 2. else 전달받은 seesion_id 로 chat_history 이력을 가져온다. 
        else: 
            chat_history_orm = chat_crud.get_chat_history(db=db, session_id=session_id)
            for msg in chat_history_orm:
                chat_history.append( {"role": msg.role ,"content": msg.content} )


        # 3. model + agent 조합으로 정해진 prompt 조합
        # get_prompt(model, self.name) from databse
        
        
        # 4. 사용자 메세지 히스토리 저장 
        # 이 대화 세션에 마지막 sequence를 가져와서 저장한다 
        last_sequence = chat_crud.get_last_sequence(db, session_id) or 0
        last_sequence += 1
        chat_crud.save_message(db,session_id,"user",message,last_sequence)

        # 5. llm 질의
        llm_reply = self._llm_reply( model, message, chat_history)

        # 6. LLM 답변 메세지 히스토리 저장 
        last_sequence += 1
        chat_crud.save_message(db,session_id,"assistant",llm_reply,last_sequence)


         # --- 6. 최종 커밋 ---
        # 이 요청에 대한 모든 DB 작업(세션 생성, 메시지 저장 2건)이 성공했으므로,
        # 트랜잭션을 최종적으로 DB에 확정(commit)합니다.
        db.commit()
        
        return llm_reply, session_id
