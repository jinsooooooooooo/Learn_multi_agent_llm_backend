from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 2단계에서 만든 설정 객체를 import 합니다.
from backend.core.config import settings

# 1. 데이터베이스 연결 "엔진" 생성
# 이 엔진은 커넥션 풀을 관리하며, 필요할 때마다 DB 연결을 제공합니다.
engine = create_engine(settings.DATABASE_URL)
# 2. 데이터베이스 "세션"을 만드는 클래스 생성
# 이 클래스를 통해 DB와 실제 대화(쿼리)를 수행하는 세션 객체를 만듭니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 3. ORM 모델의 기본이 되는 "베이스" 클래스 생성
# 나중에 우리가 만들 User, Message 같은 DB 테이블 모델들은 모두 이 Base를 상속받게 됩니다.
OrmBase = declarative_base()



# 4. 의존성 주입을 위한 DB 세션 생성기 함수
def get_db():
    """
    각 API 요청에 대한 독립적인 DB 세션을 생성하고,
    요청 처리가 끝나면 세션을 닫아주는 제너레이터(generator) 함수.
    """
    db = SessionLocal() # 1. 세션 생성 (DB 연결 풀에서 커넥션 하나를 빌려옴)
    try:
        yield db # 2. API 함수(라우트 핸들러)에게 세션을 '양보(yield)'하여 사용하게 함
    finally:
        db.close() # 3. API 함수 처리가 끝나면 (성공/실패 무관) 반드시 세션을 닫음

# Rag db는 llm_agnet_rag 연결 추가 
# rag_engine = create_engine(settings.RAG_DATABASE_URL)
# RagSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=rag_engine)
# RagOrmBase = declarative_base()

# # ----- RAG DB 세션을 얻기 위한 get_rag_db 함수 -----
# def get_rag_db():
#     db = RagSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
    
