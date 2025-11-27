# backend/core/llm_core
import os
from typing import Dict, List, Optional, AsyncGenerator, Generator
from openai import AsyncOpenAI, OpenAI
from google import genai
from google.genai import types as genai_types
# from backend.core.env_loader import load_dotenv
# env_loader 대신에 pydantic_settings로 전환
from backend.core.config import settings

# .env 파일 로드
# env_loader 대신에 pydantic_settings로 전환
#load_dotenv()
api_key = settings.OPENAI_API_KEY
default_model = settings.DEFAULT_LLM_MODEL

gemini_api_key=settings.GEMINI_API_KEY 
gemini_default_model=settings.GEMINI_DEFAULT_MODEL


client = OpenAI(api_key=api_key)
async_client = AsyncOpenAI(api_key=api_key)
clientGemini = genai.Client(api_key=gemini_api_key)



def call_gemini(model, prompt, chat_history, message) -> str:
    # 이전 히스토리로 + 신규 메세지 대화 구성
    gemini_contents = set_gemni_content(chat_history,message)

    # gemini 호출
    response = clientGemini.models.generate_content(
        model=model,
        contents = gemini_contents,
        config=genai.types.GenerateContentConfig( system_instruction=prompt )
    )
    return response.text


def call_gpt(model, prompt, chat_history, message, temperature) -> str:
    gpt_messages = set_gpt_messages(chat_history,message,prompt)

    # gpt llm 호출
    response = client.chat.completions.create(
        model=model,
        messages=gpt_messages,
        temperature=temperature,
    )

    return response.choices[0].message.content


def call_llm( model: str , prompt: str, message: str, temperature: float = 0.3, chat_history: List[Dict] = None ):
    """
    공통 LLM 호출 함수
    Argmuent:
        - model (str): 선택된 llm 모델
        - prompt (str): 시스템 role prompt 설정
        - message (str): 이번에 입력되는 사용자 메세지
        - temperature (float): 유사도 temperature
        - chat_history (List[Dict]): 현재 대화 세션에 참고해야할 이전 대화 히스토리 
    Return:
        - str
    """
    print(f'======'*20)
    print( 
        f'[llm_core.py] \n' 
        f'  - model: {model} \n'
        f'  - prompt: {prompt} \n'
        f'  - message: {message} \n'
        f'  - temperature: {temperature} \n'
        f'  - chat_history: {chat_history} \n'
        )
    print(f'======'*20)

    model = model or default_model

    llm_reply = ''
    # gemini 계열 모델의 경우 
    if model.startswith('gemini'):
        llm_reply = call_gemini(model=model, prompt=prompt, chat_history=chat_history, message=message)
        return llm_reply


    # 그 외 default = gpt 계열의 모델의 경우 
    # gpt에 전달할 마세지 리스트 프롬프트 + 이력 + 신규 메세지 순으로 추가 
    llm_reply = call_gpt(model=model, prompt=prompt, chat_history=chat_history, message=message, temperature=temperature)
    return llm_reply
      
    

async def call_llm_stream( 
        model: str , 
        prompt: str,  
        message: str, 
        temperature: float = 0.3, 
        chat_history: List[Dict] = None ) -> AsyncGenerator[str,None]:
    """
    call_llm_stream 
    """
    model = model or default_model
    # gemini model
    if model.startswith('gemini'):
        # call_gemni_stream
        async for data in call_gemini_stream(model, prompt, chat_history, message):
            yield data
    # default = gpt
    else: 
        async for data in call_gpt_stream(model, prompt, chat_history, message, temperature):
            yield data

async def call_gemini_stream(model, prompt, chat_history, message) -> AsyncGenerator[str,None]:
    # 이전 히스토리로 + 신규 메세지 대화 구성
    gemini_contents = set_gemni_content(chat_history,message)

    # 비동기 stream으로 gemini 호출
    try:
        response_stream = await clientGemini.aio.models.generate_content_stream(
            model=model,
            contents = gemini_contents,
            config=genai.types.GenerateContentConfig( system_instruction=prompt),
            # stream=True # stream 옵션 없음!!!
        )

        async for data in response_stream:
            if data.text:
                # sse_payload = data.text.replace('\n', '\ndata: ')
                # print(f'data: {sse_payload}')
                # yield f"data: {sse_payload}\n\n"
                print(f'data: {data.text}')
                yield data.text   
    except Exception as e:
        print(f"Gemini 스트리밍 중 오류: {e}")
        yield "Gemini 스트리밍 오류"
           

async def call_gpt_stream(model, prompt, chat_history, message, temperature) -> AsyncGenerator[str,None]:
    gpt_messages = set_gpt_messages(chat_history,message,prompt)

    # 비동기 stream으로 gpt llm 호출
    # OpenAI 라이브러리는 동기(sync) 스트림을 반환하므로,
    # async for 대신 일반 for 루프를 사용해도 됩니다. (단, FastAPI 라우트가 async여야 함)
    # 하지만 명시적으로 비동기를 사용하려면 별도의 라이브러리(e.g., httpx)가 필요할 수 있습니다.
    # 여기서는 openai 라이브러리의 기본 동작을 따릅니다.
    try:
        response_stream = await async_client.chat.completions.create(
            model=model,
            messages=gpt_messages,
            temperature=temperature,
            stream=True, # stream 옵션 
        )
        async for data in response_stream:
            if data.choices[0].delta.content:
                print(f'data: {data.choices[0].delta.content}')
                yield data.choices[0].delta.content
    except Exception as e:
        print(f"GPT 스트리밍 중 오류: {e}")
        yield "GPT 스트리밍 오류"        


def set_gemni_content(chat_history,message) -> list:
    gemini_contents = []
    # 히스토리로 이전 대화 구성

    if chat_history != None:
        for item in chat_history:
            gemini_contents.append(
                genai_types.Content(
                    role=item["role"] if item["role"].lower() == "user" else "model",
                    parts=[genai_types.Part(text=item["content"])]
                )
            )
    # 현재의 새로운 사용자 메시지를 가장 마지막에 추가
    gemini_contents.append(
        genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=message)]
        )
    )
    return gemini_contents


def set_gpt_messages(chat_history,message,prompt) -> list:
    gpt_messages = []

    # 제일 먼저 프롬프트 추가 
    gpt_messages.append({
        "role": 'system',
        "content": prompt
    })  
    # 현재 대화의 히스토라가 있다면 llm 메세지에 추가
    if chat_history:
        for item in chat_history:
            gpt_messages.append({
                "role": item["role"],
                "content": item["content"]
            })
    # 마지막 사용자의 신규 메시지 추가 
    gpt_messages.append({
        "role": "user",
        "content": message
    })

    return gpt_messages


