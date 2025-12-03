# 1. 베이스 이미지 생성
FROM python:3.12-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. 의존성 설치 (requirements.txt)
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스코드 복사
COPY ./backend ./backend

# 5. 통신 포트 노출
EXPOSE 8000

# 6. APP 실행 명령어
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
