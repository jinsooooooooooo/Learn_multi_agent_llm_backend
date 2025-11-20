# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware # CORSMiddleware 임포트
from backend.routes.health_check import router as health_router
from backend.routes.chat_routes import router as chat_router
from backend.routes.meeting_routes import router as meeting_router
from backend.routes.naver_news_routes import router as naver_news_router
from backend.routes.news_routes import router as news_router
from backend.routes.langchain_chat_routes import router as langchain_router
from backend.routes.langchain_chatstream_routes import router as langchain_stream_router
from backend.routes.stream_sample_routes import router as stream_sample_router
from backend.db_manager import engine


# @app.on_event("startup") #on_event(startup / shutdown) 더이상 지원하지 않아 lifespan 으로 변경
# yield 이전 -> startup: db open
# yield 이후 -> shttdown: db close
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- yield 이전: 애플리케이션 시작 시 실행될 코드 ---
    # 서버 시작 시 등록된 모든 라우트를 콘솔에 출력하는 디버그용 코드, 데이터베이스 연결 등
    print("--- Lifespan: Server is starting up! ---")
    for route in app.routes:
        methods = ', '.join(route.methods or [])
        print(f"  {route.path:30s} → [{methods}]")

    print("--- Lifespan: Connecting to database... ---")
    # 앱이 시작될 때, DB 엔진이 첫 연결을 시도하고 커넥션 풀을 준비합니다.
    # 간단한 연결 테스트를 위해 ping을 보낼 수 있습니다.
    try:
        conn = engine.connect()
        conn.close()
        print("--- Lifespan: Database connection successful. ---")
    except Exception as e:
        print(f"--- Lifespan: Database connection failed: {e} ---")


    yield

    # --- yield 이후 : 애플리케이션 종료 시 실행될 코드 ---
    # (예: 데이터베이스 연결 해제, 리소스 정리 등)
    print("--- Lifespan: Server is shutting down! ---")
    # 앱이 종료될 때, SQLAlchemy 엔진의 커넥션 풀을 정리합니다.
    engine.dispose()
    print("--- Lifespan: Database connection pool disposed. ---")


app = FastAPI(title="RAG Multi-Agent Backend",lifespan=lifespan)


app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(meeting_router, prefix="/api")
app.include_router(naver_news_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(langchain_router, prefix="/api")
app.include_router(langchain_stream_router, prefix="/api")
app.include_router(stream_sample_router, prefix="/api")

# 백엔드 (CORS 허용 추가): (React/HTML 등 외부 요청을 허용해야 합니다)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Welcome to RAG Multi-Agent Backend"}
