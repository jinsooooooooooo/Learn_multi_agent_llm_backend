# backend/core/llm_core
import os
from typing import Dict, List, Optional
from openai import OpenAI
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
clientGemini = genai.Client(api_key=gemini_api_key)


def call_gemini(model, prompt, chat_history, message):
    return None

def call_gpt(model, prompt, chat_history, message, temperature):
    return None

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

    model = model or default_model


    # gemini 계열 모델의 경우 
    if model.startswith('gemini'):
        # refactoring 예정 gemini 함수 분리
        # return call_gemini(model, prompt, chat_history, message)

        # 대화 이력(history)가 있다면 꺼내서 gooogle api 포멧에 맞게 변환 
        gemini_contents = []
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

        response = clientGemini.models.generate_content(
            model=model,
            contents = gemini_contents,
            config=genai.types.GenerateContentConfig(
                system_instruction=prompt
            )
        )
        return response.text

    # 나머지 default = gpt 계열의 모델의 경우 
    # gpt에 전달할 마세지 리스트 프롬프트 + 이력 + 신규 메세지 순으로 추가 
    
      
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

    print(f'    - gpt_messages: {gpt_messages}')

    response = client.chat.completions.create(
        model=model,
        messages=gpt_messages,
        temperature=temperature,
    )


    return response.choices[0].message.content
    # refactoring 예정 gpt 호출 함수 분리
    # return call_gpt(model, prompt, chat_history, message, temperature)