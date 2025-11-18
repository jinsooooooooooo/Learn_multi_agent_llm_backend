## RAG Multi-Agent 프로젝트

**프로젝트 설명:**

이 프로젝트는 RAG (Retrieval-Augmented Generation) 기술과 Multi-Agent 시스템을 활용하여 다양한 작업을 수행하는 것을 목표로 합니다. 현재 다음과 같은 기능을 제공합니다.

*   챗봇: 기본적인 질문 응답 기능
*   뉴스 검색: Naver News API를 이용하여 뉴스 검색 기능 제공

---

**기술 스택:**

*   Python
*   FastAPI
*   Langchain
*   Redis
*   OpenAI
*   Google Gemini

---

**설치 방법:**

1.  Python 3.8 이상 설치
2.  가상 환경 생성 (선택 사항): `python -m venv .venv`
3.  가상 환경 활성화:
    *   Linux/macOS: `source .venv/bin/activate`
    *   Windows: `.venv\Scripts\activate`
4.  패키지 설치: 
```sh
pip install -r requirements.txt`
```

---

**실행 방법:**

1. config 환경 설정:
     `.env` 파일 설정: `backend/.env` 파일을 복사하여 필요한 환경 변수를 설정합니다.
    e.g. 네이버 뉴스 API Key
    e.g. LLM 모델 key


2.  백엔드(FastAPI) 실행: 
```sh
uvicorn backend.main:app --reload`
# https://127.0.0.1:8000/docs  -> Swagger UI에서 Routes API 점검 (try out)

```
    
3. Docker + Redis 실행:
```sh
    # 먼저 Docker 실행 프로세스 확인
    docker ps -a
    # Redis 컨테이너가 Exited 상태라면: 
    docker start [Redis 컨테이너 이름 또는 ID]
    # 또는 Redis 컨테이너가 아예 없다면, 새로 실행 Docker 컨테이너 실행
    docker run --name my-redis-server -p 6379:6379 -d redis`
```
    
---

**API 엔드포인트:**

*   `/health`: 헬스 체크
*   `api/chat`: 챗봇 Agent API
*   `api/metting`: 회의실 Agent API


**Backend API 호출 시쿼스다이어긂**

```mermaid
sequenceDiagram
    %% 다이어그램 제목
    title: /api/chat 요청 처리 흐름

    %% 참여자 정의
    participant User as Frontend/Client
    participant Routes as chat_routes.py
    participant Agent as chat_agent.py
    participant DB as db_manager.py
    participant Core as llm_core.py

    %% 1. 클라이언트 요청 시작
    User->>Routes: POST /api/chat 
    activate Routes

    %% 2. Agent에게 처리 위임
    Routes->>Agent: handle(session_id, user_id, model, message)
    activate Agent

    %% 3. Agent가 세션 ID 관리 (핵심 로직 1)
    alt session_id가 없는 경우 
        Agent->>DB: 새로운 session insert
        Activate DB
        DB-->>Agent: 생성된 id 반환 uuid : (session_id)
        Deactivate DB
    end
    note right of Agent: 이제부터 session_id는 항상 존재함

    %% 4. Agent가 DB에서 대화 이력 조회
    Agent->>DB: fetch_history(session_id)
    activate DB
    DB-->>Agent: 대화 이력 반환: List[{role},{content}]
    deactivate DB

    %% 5. Agent + model 조함의 프롬프트 조합
    Agent->>DB: get_prompt(model, agent)
    activate DB
    DB-->>Agent: prompt 반환: (str)
    deactivate DB
    
    Agent->>Agent: 시스템 프롬프트 + 대화 이력 + 새 메시지 조합

    %% 6. Agent가 llm_core에 LLM 호출 요청
    Agent->>Core: call_llm(model, prompt, messages, history)
    activate Core

    %% 7. llm_core가 모델에 따라 분기 처리 (핵심 로직 2)
    
    %% 프롬프트+메세지+히스토리 조합
    Core ->> Core: 프롬프트+메세지+히스토리 조합
    alt model이 'gemini'인 경우
        Core->>Core: Gemini API 호출
    else model이 'gpt'인 경우
        Core->>Core: OpenAI API 호출
    end
    
    Core-->>Agent: LLM 응답 (reply_text) 반환
    deactivate Core
    
    %% 8. Agent가 새로운 대화 내용을 DB에 저장
    Agent->>DB: save_history(session_id, user_message, ai_reply)
    activate DB
    DB-->>Agent: 저장 완료
    deactivate DB

    %% 9. Agent가 최종 결과(세션ID, 응답)를 Routes에 반환
    Agent-->>Routes: (session_id, reply_text) 반환
    deactivate Agent

    %% 10. Routes가 최종 응답 생성 및 전송
    Routes->>Routes: ChatResponse JSON 생성
    Routes-->>User: {"agent": ..., "session_id": ..., "reply": ...}
    deactivate Routes

```

**기여 방법:**



**라이선스:**

