from backend.agents.base_agent import BaseAgent
from backend.core.chat_memory import get_conversation_chain
from backend.core.env_loader import REDIS_HOST, REDIS_PORT, REDIS_DB
from langchain_openai import ChatOpenAI
from langchain_classic.callbacks.base import BaseCallbackHandler
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

class StreamCallbackHandler(BaseCallbackHandler):
    """LLM 응답을 스트리밍으로 전송하는 콜백 핸들러"""
    def __init__(self, send):
        self.send = send

    def on_llm_new_token(self, token, **kwargs):
        self.send(token)

class LangchainChatStreamAgent(BaseAgent):
    """
    Redis 기반 LangChain Streaming Agent
    """

    def __init__(self, user_id: str = "guest"):
        super().__init__(
            name="LangchainChatStreamAgent",
            role_prompt="Streaming 기반 대화형 AI 비서"
        )
        self.user_id = user_id

    def handle_stream(self, user_input: str):
        """스트리밍 방식으로 응답 전송 (generator)"""

        redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        history = RedisChatMessageHistory(chat_id=f"user:{self.user_id}", url=redis_url, ttl=3600)
        memory = ConversationBufferMemory(chat_memory=history, return_messages=True)

        def event_stream():
            # 클라이언트로 실시간 전송할 yield generator
            def send(token):
                yield f"data: {token}\n\n"

            # LangChain의 Streaming Callback 설정
            callback = StreamCallbackHandler(lambda token: (yield f"data: {token}\n\n"))
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                streaming=True,
                callbacks=[callback],
            )

            chain = ConversationChain(llm=llm, memory=memory, verbose=False)
            chain.run(input=user_input)
            yield "data: [DONE]\n\n"

        return event_stream()
    
    def handle(self, user_input: str) -> str:
        """
        (구현 필요) 추상 메서드 handle 구현
        """
        return "This Agent only supports streaming"
