from sqlalchemy import func, text
from sqlalchemy.orm import Session
import uuid

# 우리가 6단계에서 만든 모델 클래스들을 import 합니다.
from backend.database.models.chat_model import ChatSession, SessionMessage


# ----------------------------------------------- 
# ------- Chat Session 대하 생성 (첫 대화) ---------- 
def create_chat_session(db: Session, user_id: str, agent_id: str, model_id: str) -> ChatSession:
    """
    새로운 채팅 세션을 생성하고 DB에 저장합니다.
    - Args:
        db (Session): 데이터베이스 세션 객체.
        user_id (str): 사용자 ID.
        agent_id (str): 사용된 에이전트 ID.
        model_id (str): 사용된 모델 ID.
    - Returns:
        ChatSession: 새로 생성된 ChatSession 객체.
    """
    # 1. 모델 클래스를 사용하여 파이썬 객체를 만듭니다.
    #    session_id는 DB에서 자동으로 생성되므로 값을 주지 않습니다.
    new_session = ChatSession(
        user_id=user_id,
        agent_id=agent_id,
        model_id=model_id
    )
    # 2. 이 객체를 세션에 '추가(add)'합니다. 아직 DB에 저장된 것은 아닙니다.
    db.add(new_session)
    # 3. 세션의 변경사항을 DB에 '커밋(commit)'하여 최종 저장합니다.
    db.commit()
    # 4. DB에 저장되면서 할당된 session_id 등을 포함한 객체를 '새로고침(refresh)'하여 반환합니다.
    db.refresh(new_session)
    return new_session


# -----------------------------------------------
# ------- Chat Session 단일 조회 ---------- 
def get_chat_session(db: Session, session_id: uuid.UUID) -> ChatSession | None:
    """
    주어진 session_id로 채팅 세션을 조회합니다.
    """
    # db.query(모델)로 조회 시작. .filter()로 조건 지정. .first()로 첫 번째 결과만 가져옴.
    # 결과가 없으면 None을 반환합니다.
    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()


# -----------------------------------------------
# ------- Chat Session 히스토리 불러오기 ---------- 
def get_chat_history(db: Session, session_id: uuid.UUID) -> list[SessionMessage]:
    """
    주어진 session_id에 속한 모든 메시지를 시간 순서대로 조회합니다.
    - Args:
        db:
        session_id:
    - Returns:
        lst[SessionMessage]
    """
    return db.query(SessionMessage)\
             .filter(SessionMessage.session_id == session_id)\
             .order_by(SessionMessage.sequence.asc())\
             .all()


# -----------------------------------------------
# ------- message 히스토리 저장하기 ---------- 
def save_message(db: Session, session_id: uuid.UUID, role: str, content: str ) -> SessionMessage:
    """
    새로운 채팅 메시지를 생성하고 DB에 저장합니다.
    - Args:
        db:
        seesion_id:
        role:
        content:
    - Returns:
        SessionMessage: 저장된 메세지 반환
    """
    # 메세지 이력을 저장 할 때는 같은 seesion 안에서 seq를 순차적으로 증가시켜야 하므로 단순한 add() 만으로는 구현 불가

    # 방법1: 직접 Query 직성
    # INSERT ... SELECT 구문을 직접 작성
    # query = text("""
    #     insert into llm_agent.session_message
    #     ( session_id, "role", "content", "sequence" )
    #     VALUES (
    #         :session_id,
    #         :role,
    #         :content,
    #         (SELECT COALESCE(MAX(sequence), 0) + 1 FROM llm_agent.session_message WHERE session_id = :session_id)
    #     )
    #     RETURNING *; -- INSERT된 전체 레코드를 반환            
    # """)

    # # db.execute()는 CursorResult 객체를 반환합니다.
    # result_cursor = db.execute(
    #     query, 
    #     {"session_id": session_id, "role": role, "content": content}
    # ).fetchone()

    # return result_cursor

    # 방법2. 현재 세션의 최대 'sequence' 값을 조회합니다.
    #    -> SQL: SELECT max(sequence) FROM llm_agent.session_message WHERE session_id = :session_id
    last_sequence = db.query(func.max(SessionMessage.sequence))\
                      .filter(SessionMessage.session_id == session_id)\
                      .scalar()
    #    조회된 최대값이 없으면(첫 메시지) 1로, 있으면 +1을 합니다.
    next_sequence = last_sequence + 1 if last_sequence else 1
    #    계산된 'next_sequence'를 사용하여 새 메시지 객체를 만듭니다.
    new_message = SessionMessage(
        session_id=session_id,
        role=role,
        content=content,
        sequence=next_sequence
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)


