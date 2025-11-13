# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # CORSMiddleware 임포트
from routes.health_check import router as health_router
from routes.chat_routes import router as chat_router
from routes.meeting_routes import router as meeting_router
from routes.naver_news_routes import router as naver_news_router
from routes.news_routes import router as news_router
from routes.langchain_chat_routes import router as langchain_router
from routes.langchain_chatstream_routes import router as langchain_stream_router
from routes.stream_sample_routes import router as stream_sample_router


app = FastAPI(title="RAG Multi-Agent Backend")
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(meeting_router, prefix="/api")
app.include_router(naver_news_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(langchain_router, prefix="/api")
app.include_router(langchain_stream_router, prefix="/api")
app.include_router(stream_sample_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to RAG Multi-Agent Backend"}


@app.on_event("startup")
def on_startup():
    # 서버 시작 시 등록된 모든 라우트를 콘솔에 출력하는 디버그용 코드
    print("\n Registered Routes:")
    for route in app.routes:
        methods = ', '.join(route.methods or [])
        print(f"  {route.path:30s} → [{methods}]")

# 백엔드 (CORS 허용 추가): (React/HTML 등 외부 요청을 허용해야 합니다)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

