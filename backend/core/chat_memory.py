# backend/core/chat_memory.py
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from backend.core.env_loader import REDIS_HOST, REDIS_PORT, REDIS_DB


def get_conversation_chain(user_id: str):
    """
    Redis 기반 LangChain Memory + ConversationChain 생성기
    LangChain 1.x (classic + community) 버전 기준
    """

    # 1️⃣ Redis 연결 URL 구성
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # 2️⃣ Redis에 대화 이력 관리 (최신 10개 자동 유지)
    history = RedisChatMessageHistory(
        chat_id=f"user:{user_id}",
        url=redis_url,
        ttl=3600  # 1시간 TTL
    )

    # 3️⃣ Memory 구성 — LangChain의 ConversationBufferMemory
    memory = ConversationBufferMemory(
        chat_memory=history,
        return_messages=True  # 반드시 True로 설정
    )

    # 4️⃣ LLM 초기화 — OpenAI Chat Model 사용
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    # 5️⃣ LLM + Memory를 결합한 ConversationChain
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    return chain