# backend/agnet/chat_agent.py
from sqlalchemy import func
from backend.agents.base_agent import BaseAgent
from sqlalchemy.orm import Session

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

    def handle(self, db: Session, session_id: str, user_id: str, model: str, message: str) -> tuple[str, str]:
        """
        사용자 메시지를 처리하고, DB와 연동하여 대화 이력을 관리합니다.
        모든 DB 작업은 단일 트랜잭션으로 처리됩니다.
        """
        try:
            # --- 1. 세션 확인 및 생성 ---
            current_session_id = session_id # 전달받은 session_id를 사용 또는 갱신할 변수

            if current_session_id is None or current_session_id.strip() == "":
                print("[Agent] New session needed. Creating one...")
                new_session_obj = chat_crud.create_chat_session(
                    db=db, 
                    user_id=user_id, 
                    agent_id=self.name, 
                    model_id=model
                )
                current_session_id = new_session_obj.session_id # 새로 생성된 ID로 업데이트
                # print(f"[Agent] New session created with ID: {current_session_id}")
                chat_history_orm = [] # 새 세션이므로 이력은 비어있습니다.
            else:
                print(f"[Agent] Existing session. Fetching history for ID: {current_session_id}")
                chat_history_orm = chat_crud.get_chat_history(db=db, session_id=current_session_id)
                
            # --- 2. LLM 호출을 위한 데이터 준비 ---
            # DB에서 가져온 ORM 객체 리스트를, LLM이 이해할 수 있는 dict 리스트로 변환합니다.
            chat_history_dict = [{"role": msg.role, "content": msg.content} for msg in chat_history_orm]

            # --- 3. 사용자 메시지 저장 ---
            # 다음 sequence 번호를 가져와서 사용자 메시지를 저장합니다.
            next_sequence = chat_crud.get_last_sequence(db=db, session_id=current_session_id) + 1
            chat_crud.save_message(
                db=db, 
                session_id=current_session_id, 
                role="user", 
                content=message,
                sequence=next_sequence # sequence 파라미터 전달
            )
            
            # --- 4. LLM 호출 ---
            print("[Agent] Calling LLM...")
            llm_reply = self._llm_reply(
                model=model, 
                message=message, 
                chat_history=chat_history_dict
            )
            print("[Agent] LLM reply received.")

            # --- 5. LLM 응답 저장 ---
            # 다음 sequence 번호를 가져와서 LLM 응답을 저장합니다.
            next_sequence += 1
            chat_crud.save_message(
                db=db, 
                session_id=current_session_id, 
                role="assistant", 
                content=llm_reply,
                sequence=next_sequence # sequence 파라미터 전달
            )

            # --- 6. 최종 커밋 ---
            # 이 요청에 대한 모든 DB 작업이 성공했으므로, 트랜잭션을 최종 확정합니다.
            print("[Agent] Committing transaction to DB.")
            db.commit()

            return llm_reply, str(current_session_id) # UUID 객체이므로 str()로 변환

        except Exception as e:
            # --- 예외 발생 시 롤백 ---
            print(f"[Agent] An error occurred during handle: {e}")
            db.rollback() # 모든 DB 변경사항을 "없던 일로" 되돌립니다.
            raise e
