# 1. Builder: 의존성 설치와 빌드 아티팩트를 준비하는 단계 ---
FROM python:3.12-slim 

# 2. 작업 디렉토리
WORKDIR /app

# 3. 의존성 설치 (requirements.txt)
COPY ./requirements.txt .

# 4. 시스템 빌드 도구가 필요하면 여기서만 설치. 설치 후 apt 캐시를 즉시 제거해 레이어를 줄입니다.
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc libpq-dev libxml2-dev libxslt-dev \
  && rm -rf /var/lib/apt/lists/*

# 5. venv에 패키지를 설치하면 런타임 이미지로 복사하기 쉬움.
RUN python -m venv /opt/venv \
  && /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel \
  && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 3. PATH에 venv를 넣어 python / pip가 해당 환경을 사용하도록 함
ENV PATH="/opt/venv/bin:$PATH"

# 5. 소스는 마지막에 복사해서 의존성 레이어를 재사용하게 함
COPY ./backend ./backend
# COPY ./pyproject.toml ./pyproject.toml

# 5. 통신 포트 노출
EXPOSE 8000

# 6. APP 실행 명령어
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
