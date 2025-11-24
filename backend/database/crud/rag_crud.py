# backend/database/crud/rag_crud.py
from sqlalchemy.orm import Session
from typing import List, Dict

# 1. 우리가 만든 RAG 모델 클래스들을 import 합니다.
from backend.database.models.rag_model import RagSources, RagDocumentChunks, RagVectorsMinilm, RagVectorsGemini

def get_all_sources(db: Session) -> List[RagSources]:
    """
    rag_sources 테이블에 있는 모든 문서 메타데이터를 조회합니다.
    NCP object의 메타 데이터와 변경 내용을 비교하기 위함
    Args:
        - None
    Retursn:
        - List[RagSources]: 
    """
    return db.query(RagSources).all()

def bulk_insert_chunks_and_vectors(
    db: Session,
    source: RagSources,
    chunks_data: List[Dict]
):
    """
    하나의 문서에서 분할된 여러 청크와 벡터들을 한 번에 DB에 저장합니다.
    (Bulk Insert)
    """
    # 딕셔너리 리스트 형태의 청크 데이터로부터 ORM 객체 리스트를 생성합니다.
    chunks_to_add = []
    vectors_minilm_to_add = []
    vectors_gemini_to_add = []

    for chunk_item in chunks_data:
        # 1. RagDocumentChunks 객체 생성
        new_chunk = RagDocumentChunks(
            document_id=source.document_id,
            chunk_text=chunk_item['text'],
            sequence_num=chunk_item['sequence'],
            chunk_metadata=chunk_item['metadata']
        )
        # RagDocumentChunks에 먼저 저장을 하고 flush() 해야 chunk_id를 알 수 있다.
        # chunks_to_add.append(new_chunk)
        db.add(new_chunk)
        db.flush()

        print(f'new_chunk.chunk_id: {new_chunk.chunk_id}')

        # 2. RagVectorsMinilm 객체 생성 (벡터가 있는 경우)
        if 'vector_minilm' in chunk_item:
            vectors_minilm_to_add.append(
                RagVectorsMinilm(
                    chunk_id=new_chunk.chunk_id,
                    embedding_vector=chunk_item['vector_minilm']
                )
            )

        # 3. RagVectorsGemini 객체 생성 (벡터가 있는 경우)
        if 'vector_gemini' in chunk_item:
            vectors_gemini_to_add.append(
                RagVectorsGemini(
                    chunk_id=new_chunk.chunk_id,
                    embedding_vector=chunk_item['vector_gemini']
                )
            )

    # SQLAlchemy의 bulk_save_objects를 사용하여 여러 객체를 한 번의 쿼리로 효율적으로 저장합니다.
    # if chunks_to_add:
    #     db.bulk_save_objects(chunks_to_add)
    #     db.flush()
    if vectors_minilm_to_add:
        db.bulk_save_objects(vectors_minilm_to_add)
    if vectors_gemini_to_add:
        db.bulk_save_objects(vectors_gemini_to_add)

    # 참고: bulk 작업은 ORM의 관계(relationship) 자동 동기화 같은 기능이
    # 일부 제한될 수 있지만, 대량 삽입 시에는 훨씬 빠릅니다.