from sqlalchemy import UUID, Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.database.db_manager import OrmBase


# ===================================================================
# ChatSession 모델: llm_agent.chat_session 테이블과 매핑됩니다.
# ===================================================================
class ChatSession(OrmBase):
    # __tablename__: SQLAlchemy에게 이 클래스가 어떤 테이블과 연결되는지 알려줍니다.
    # __table_args__: 테이블에 대한 추가 설정을 정의합니다.
    # {'schema': 'llm_agent'}: PostgreSQL의 'llm_agent' 스키마 안에 이 테이블이 있음을 명시합니다.
    __tablename__ = 'chat_session'
    __table_args__ = {'schema': 'llm_agent'}


    # --- 컬럼(Column) 정의 ---
    # 각 클래스 변수는 테이블의 컬럼 하나와 일대일로 매핑됩니다.

    # session_id: uuid 타입의 기본 키(Primary Key)입니다.
    # DB에 이미 DEFAULT gen_random_uuid()가 설정되어 있으므로, 여기선 default 옵션을 주지 않습니다.
    # SQLAlchemy는 INSERT 시 이 컬럼을 생략하고, DB가 값을 채우도록 합니다.
    session_id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid")

     # user_id: varchar(50) 타입의 문자열이며, 비어있을 수 없습니다(nullable=False).
    user_id = Column(String(50), nullable=False)
    agent_id = Column(String(50), nullable=False)
    model_id = Column(String(50), nullable=False)

    # title: varchar(255) 타입의 문자열이며, 비어있어도 됩니다(nullable=True가 기본값).
    title = Column(String(255))

    # start_time: 타임존 정보가 있는 시간 타입입니다.
    # server_default=func.now()는 데이터베이스에 레코드가 INSERT될 때 DB의 현재 시간을 자동으로 기록해줍니다.
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))


    # --- 관계(Relationship) 정의 ---
    # 이것은 DB에 실제 컬럼을 만드는 것이 아니라, ORM(SQLAlchemy)에게 객체 간의 연결을 알려주는 설정입니다.
    # 'ChatSession' 객체 하나는 여러 개의 'SessionMessage' 객체를 가질 수 있습니다.
    messages = relationship(
        "SessionMessage",               # 연결될 상대방 클래스의 이름입니다.
        back_populates="session",       # 상대방(SessionMessage)의 'session' 속성과 서로 연결되어 있음을 명시합니다.
        primaryjoin="ChatSession.session_id == SessionMessage.session_id",   #<클래스>.<속성> 으로 표현하여 join key 매핑
        cascade="all, delete-orphan"    # ChatSession이 삭제될 때, 관련된 모든 SessionMessage도 함께 삭제되도록 하는 중요한 옵션입니다.
    )


# ===================================================================
# SessionMessage 모델: llm_agent.session_message 테이블과 매핑됩니다.
# ===================================================================
class SessionMessage(OrmBase):
    __tablename__ = 'session_message'
    __table_args__ = {'schema': 'llm_agent'}
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    # session_id: 이 메시지가 어떤 ChatSession에 속하는지를 가리키는 외래 키(Foreign Key)입니다.
    # ForeignKey('llm_agent.chat_session.session_id')는 DB 레벨에서 두 테이블 간의 관계를 강제합니다
    session_id =  Column(UUID(as_uuid=True), ForeignKey('llm_agent.chat_session.session_id'), nullable=False)
    sequence = Column(Integer, nullable=False)
    role = Column(String[10], nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()")

     # --- 관계(Relationship) 정의 ---
    # 'SessionMessage' 객체는 하나의 'ChatSession' 객체에 속합니다.
    session = relationship(
        "ChatSession",                  # 연결될 상대방 클래스의 이름입니다.
        back_populates="messages"       # 상대방(ChatSession)의 'messages' 속성과 서로 연결되어 있음을 명시합니다.
    )
