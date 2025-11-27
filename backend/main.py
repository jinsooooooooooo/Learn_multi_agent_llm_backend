# main.py
import logging
import time
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse # CORSMiddleware 임포트

from backend.database.db_manager import engine
from backend.core.config import settings


from backend.routes.health_check import router as health_router
from backend.routes.chat_routes import router as chat_router
from backend.routes.meeting_routes import router as meeting_router
from backend.routes.naver_news_routes import router as naver_news_router
from backend.routes.news_routes import router as news_router
from backend.routes.langchain_chat_routes import router as langchain_router
from backend.routes.langchain_chatstream_routes import router as langchain_stream_router
from backend.routes.stream_sample_routes import router as stream_sample_router
from backend.routes.models_routes import router as models_router
from backend.routes.rag_routes import router as rag_router
from backend.routes.stream_test_routes import router as stream_test_router



# 로거 설정 (파일 상단에 추가)
logging.basicConfig(level=logging.INFO, force=True) 
logger = logging.getLogger(__name__)


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
app.include_router(models_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(stream_test_router, prefix="/api")



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






# logging 
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    
    start_time = time.time()
    
    # 다음 핸들러(라우트 등)를 호출
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000  # ms 단위로 변환
    # 기본 로그 Info
    logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Response: {response.status_code} | "
            f"Processed in: {process_time:.2f}ms"
        )
    # local 또는 dev 환경에서만 추가적인 상세 정보를 DEBUG 레벨로 기록
    if settings.APP_ENV in ("local", "dev"):
        # debug1: 요청을 보낸 클라이언트의 IP 주소
        client_host = request.client.host
        logger.info(f"    - Client IP: {client_host}")
        # debug2: 요청에 포함된 헤더 정보 (User-Agent, Authorization 등)
        user_agent = request.headers.get("user-agent", "N/A")
        logger.info(f"    - User-Agent: {user_agent}")
        
    
    return response


# --- 전역 예외 핸들러 추가 ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    처리되지 않은 모든 예외를 잡아 로깅하고,
    일관된 형식의 500 에러 응답을 반환합니다.
    """
    # 1. 서버 로그에 상세한 에러 정보 기록
    logger.error(
        f"Unhandled error during request: {request.method} {request.url.path}",
        exc_info=True  # 스택 트레이스를 함께 기록
    )

    # 2. 사용자에게 통일된 형식의 에러 메시지 제공
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "서버 내부에서 예상치 못한 오류가 발생했습니다. 관리자에게 문의해주세요."
            }
        },
    )
