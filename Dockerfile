# 1. Builder: 의존성 설치와 빌드 아티팩트를 준비하는 단계 ---
FROM python:3.12-slim AS builder

# 2. 작업 디렉토리
WORKDIR /app

# 3. 의존성 설치 (requirements.txt)
COPY ./requirements.txt .

# 4. 시스템 빌드 도구가 필요하면 여기서만 설치. 설치 후 apt 캐시를 즉시 제거해 레이어를 줄입니다.
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# 5. venv에 패키지를 설치하면 런타임 이미지로 복사하기 쉬움.
RUN python -m venv /opt/venv \
  && /opt/venv/bin/python -m pip install --upgrade pip \
  && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# OPTIONAL (권장): 빌드 시점에 Import 오류/컴파일 오류를 조기 검출 ---
# CI/빌드에서 실패하도록 하려면 아래 RUN을 활성화 하세요.
# COPY ./import_check.py .
# RUN /opt/venv/bin/python -m compileall . \
#  && /opt/venv/bin/python ./import_check.py


# --- Runtime: 실제 서비스 이미지를 가볍게 만드는 단계 ---
FROM python:3.12-slim AS runtime

# 1. 런타임에 필요한 최소 시스템 패키지만 설치
RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq5 ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# 2. 빌더에서 만든 가상환경을 복사 (패키지와 pip 등 포함)
COPY --from=builder /opt/venv /opt/venv

# 3. PATH에 venv를 넣어 python / pip가 해당 환경을 사용하도록 함
ENV PATH="/opt/venv/bin:$PATH"

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. 소스는 마지막에 복사해서 의존성 레이어를 재사용하게 함
COPY ./backend ./backend
# COPY ./pyproject.toml ./pyproject.toml

# 4. 소스코드 복사
COPY ./backend ./backend
# COPY ./pyproject.toml ./pyproject.toml

# 5. 통신 포트 노출
EXPOSE 8000

# 6. APP 실행 명령어
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
