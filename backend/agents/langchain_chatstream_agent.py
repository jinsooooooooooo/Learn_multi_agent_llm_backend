# backend\agents\langchain_chatstream_agent.py
import asyncio
from queue import Queue
from threading import Thread
from agents.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
from langchain_classic.callbacks.base import BaseCallbackHandler
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from core.env_loader import REDIS_HOST, REDIS_PORT, REDIS_DB

class QueueCallbackHandler(BaseCallbackHandler):
    """LLM 응답을 Queue에 저장하는 콜백 핸들러"""
    def __init__(self, queue: Queue):
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """새로운 토큰을 큐에 넣습니다."""
        self.queue.put(token)

    def on_llm_end(self, *args, **kwargs) -> None:
        """LLM 작업이 끝나면 큐에 종료 신호를 넣습니다."""
        self.queue.put(None)

class LangchainChatStreamAgent(BaseAgent):
    """
    Redis 기반 LangChain Streaming Agent (Queue 사용)
    """
    def __init__(self, user_id: str = "guest"):
        super().__init__(
            name="LangchainChatStreamAgent",
            role_prompt="Streaming 기반 대화형 AI 비서"
        )
        self.user_id = user_id

    async def handle_stream(self, user_input: str):
        """스트리밍 방식으로 응답 전송 (async generator)"""
        q = Queue()

        redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        history = RedisChatMessageHistory(session_id=f"user:{self.user_id}", url=redis_url, ttl=3600)
        memory = ConversationBufferMemory(chat_memory=history, return_messages=True)

        # 백그라운드 스레드에서 실행될 작업
        def run_chain_in_thread():
            callback = QueueCallbackHandler(q)
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                streaming=True,
                callbacks=[callback],
            )
            chain = ConversationChain(llm=llm, memory=memory, verbose=False)
            chain.run(input=user_input)

        # 스레드 시작
        thread = Thread(target=run_chain_in_thread)
        thread.start()

        # 큐에서 데이터를 기다리고 yield
        while True:
            token = await asyncio.to_thread(q.get)
            if token is None:
                # 종료 신호 수신
                break
            yield f"data: {token}\n\n"
        
        yield "data: [DONE]\n\n"

    def handle(self, user_input: str) -> str:
        return "This Agent only supports streaming"