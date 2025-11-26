# 1. db_manager에서 engine과 OrmBase를 가져옵니다.
from backend.database.db_manager import engine, rag_engine, OrmBase, RagOrmBase

# 2. 👇 가장 중요한 부분! 👇
# SQLAlchemy가 테이블을 생성하려면, 어떤 모델들이 있는지 알아야 합니다.
# 따라서 우리가 만든 모든 모델 클래스가 들어있는 파일을 여기서 반드시 import 해야 합니다.
# 이 import 구문이 없으면, OrmBase는 어떤 자식 클래스가 있는지 몰라서 아무 테이블도 만들지 않습니다.
from backend.database.models import agent_model, chat_model, rag_model

print("Creating tables...")

# 3. OrmBase.metadata.create_all(bind=engine)
# OrmBase에 연결된 모든 모델(AgentInfo, Chats 등)을 찾아서,
# 'engine'에 연결된 데이터베이스에 테이블을 생성합니다.
# 이미 테이블이 존재하면, 아무 작업도 하지 않아 안전합니다.
OrmBase.metadata.create_all(bind=engine)

# RagOrmBase.metadata.create_all(bind=rag_engine)

print("Tables created successfully.")