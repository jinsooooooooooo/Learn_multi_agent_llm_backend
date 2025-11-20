from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # .env 파일을 읽어서 환경 변수를 로드하도록 설정합니다.
    # 만약 .env 파일이 없다면, 시스템 환경 변수에서 직접 값을 찾습니다.
    # (이것이 K8s 환경에서 빛을 발하는 부분입니다!)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 여기에 필요한 모든 환경 변수를 "타입 힌트"와 함께 정의합니다.
    # pydantic이 자동으로 .env 파일에서 이 변수 이름(대소문자 무시)을 찾아 값을 채워줍니다.
    DATABASE_URL: str

    # OpenAI 설정
    OPENAI_API_KEY: str
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"

    # Google Geminai 설정
    GEMINI_API_KEY: str
    GEMINI_DEFAULT_MODEL: str="gemini-2.0-flash"

    # FastAPI settings
    APP_NAME:str 
    APP_ENV:str 

    # Redis settings
    REDIS_HOST:str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Naver API 
    NAVER_CLIENT_ID: str 
    NAVER_CLIENT_SECRET: str


# 설정 클래스의 인스턴스를 만들어 다른 파일에서 쉽게 가져다 쓸 수 있도록 합니다.
settings = Settings()