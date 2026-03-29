import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# 먼저 APP_ENV 환경 변수를 읽어옵니다. 기본값은 'dev'로 설정할 수 있습니다.
# 1. 어떤 .env 파일을 읽을지 결정하는 "메타-설정" (이전과 동일)
app_env = os.getenv("APP_ENV", "local")
env_file = f".env.{app_env}"


class Settings(BaseSettings):
    # .env 파일을 읽어서 환경 변수를 로드하도록 설정합니다.
    # 만약 .env 파일이 없다면, 시스템 환경 변수에서 직접 값을 찾습니다.
    # (이것이 K8s 환경에서 빛을 발하는 부분입니다!)
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8")

    # 여기에 필요한 모든 환경 변수를 "타입 힌트"와 함께 정의합니다.
    # pydantic이 자동으로 .env 파일에서 이 변수 이름(대소문자 무시)을 찾아 값을 채워줍니다.
    DATABASE_URL: str
    # RAG_DATABASE_URL: str

    # OpenAI 설정
    OPENAI_API_KEY: str
    DEFAULT_LLM_MODEL: str = "gpt-5-nano"

    # Google Geminai 설정
    GEMINI_API_KEY: str
    GEMINI_DEFAULT_MODEL: str="gemini-2.0-flash-lite-preview-0924"

    # FastAPI settings
    APP_NAME:str 
    # 현재 어떤 환경인지 명확히 알 수 있도록 APP_ENV도 설정에 포함시킵니다.
    APP_ENV: str = app_env

    # Redis settings
    REDIS_HOST:str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Naver API 
    NAVER_CLIENT_ID: str 
    NAVER_CLIENT_SECRET: str

    # NCP Object Storage
    NCP_ACCESS_KEY:str
    NCP_SECRET_KEY:str
    NCP_REGION:str
    NCP_OBJECT_STORAGE_ENDPOINT:str
    NCP_BUCKET_NAME:str
   


# 설정 클래스의 인스턴스를 만들어 다른 파일에서 쉽게 가져다 쓸 수 있도록 합니다.
settings = Settings()


# 실행 환경을 명확히 보여주는 로그 추가 (선택 사항이지만 매우 유용)
print(f"[{settings.APP_NAME}] Running in '{settings.APP_ENV}' mode. Loaded settings from '{env_file if os.path.exists(env_file) else 'System Environment Variables'}'")
