
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 1. DB 세션을 주입해주는 get_db 함수를 import 합니다.
from backend.database.db_manager import get_db
# 2. 방금 우리가 만든 CRUD 함수를 import 합니다.
from backend.database.crud import chat_crud

# 3. 새로운 APIRouter 인스턴스를 생성합니다.
#    tags는 API 문서(Swagger UI)에서 API들을 그룹핑하는 역할을 합니다.
router = APIRouter()


# 4. GET /models 엔드포인트를 정의합니다.
#    response_model=List[str]는 이 API가 ["model1", "model2"] 형태의
#    문자열 배열을 반환할 것이라고 FastAPI에게 알려주어, 자동 문서화 및 유효성 검사를 돕습니다.
@router.get("/models", response_model=List[str])
async def get_models(db:Session = Depends(get_db) ):
    """
    현재 사용 가능한(활성화된) 모든 LLM 모델의 ID 목록을 반환합니다.
    """
    # 5. CRUD 함수를 호출하여 실제 데이터를 가져옵니다.
    #   가져온 데이터를 반환합니다. FastAPI가 자동으로 JSON 형식으로 변환해줍니다.
    return chat_crud.get_active_models(db)