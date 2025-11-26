# backend/database/crud/rag_crud.py
from sqlalchemy.orm import Session
from typing import List, Dict
from sqlalchemy import text

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

def delete_rag_source(db: Session, source_identifier: str) :
    """
    source_identifier를 기준으로 RAG 소스와 관련된 모든 데이터를 삭제합니다.
    SQLAlchemy ORM의 bulk delete 기능을 사용합니다.
    """
    # 1. 삭제할 RagSources 객체를 조회합니다.
    #    .delete()는 조회된 결과에 대해 DELETE 구문을 실행합니다.
    #    synchronize_session=False는 세션과 동기화하는 오버헤드를 줄여 성능을 향상시킵니다.
    deleted_rows = db.query(RagSources).filter(RagSources.source_identifier == source_identifier).delete()
    db.flush()
    print(f"'{source_identifier}' 소스를 삭제했습니다. (영향 받은 row: {deleted_rows})")
    return deleted_rows


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
    

    # rag_docuemnt_chunks 먼저 insert 하여 chunk_id 가져오기 
    for chunk_item in chunks_data:
        chunks_to_add.append(
            RagDocumentChunks(
                document_id=source.document_id,
                chunk_text=chunk_item['text'],
                sequence_num=chunk_item['sequence'],
                chunk_metadata=chunk_item['metadata']
            )
        )   

    db.bulk_save_objects(chunks_to_add, return_defaults=True)
    print(f"{len(chunks_to_add)}개의 청크를 DB에 저장했습니다.")

    vectors_minilm_to_add = []
    vectors_gemini_to_add = []

    for i, chunk_orm in enumerate(chunks_to_add):
        chunk_item = chunks_data[i]

        # 2. RagVectorsMinilm 객체 생성 (벡터가 있는 경우)
        if 'vector_minilm' in chunk_item:
            vectors_minilm_to_add.append(
                RagVectorsMinilm(
                    chunk_id=chunk_orm.chunk_id,
                    embedding_vector=chunk_item['vector_minilm']
                )
            )

        # 3. RagVectorsGemini 객체 생성 (벡터가 있는 경우)
        if 'vector_gemini' in chunk_item:
            vectors_gemini_to_add.append(
                RagVectorsGemini(
                    chunk_id=chunk_orm.chunk_id,
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




 # ----- vector 유사한 chuk 검사

def search_similar_chunks(
    db: Session,
    user_id: str,  
    query_text:str,
    query_vector: List[float],
    model_type: str = "minilm",
    top_k: int = 20,
    similarity_threshold: float = 0.7
) -> List[Dict]:
    """
    주어진 쿼리 벡터와 가장 유사한 문서 청크를 DB에서 검색합니다.
    (개선) 하이브리드 검색: 벡터 유사도와 키워드(LIKE) 검색을 결합하여 문서 청크를 검색합니다

    Args:
        db (Session): SQLAlchemy DB 세션.
        query_vector (List[float]): 사용자의 질문을 임베딩한 벡터.
        model_type (str): 검색에 사용할 벡터 모델 종류 ('minilm' 또는 'gemini').
        top_k (int): 반환할 가장 유사한 청크의 개수.

    Returns:
        List[Dict]: 각 청크의 텍스트, 유사도 점수, 소스 파일 정보가 담긴 딕셔너리 리스트.
             "text": item.chunk_text,
             "similarity": item.similarity,
             "source_identifier": item.source_identifier ,
    """

    

     # 사용할 벡터 테이블과 벡터 칼럼을 동적으로 선택합니다.
    if model_type == "minilm":
        vector_table = RagVectorsMinilm
    elif model_type == "gemini":
        vector_table = RagVectorsGemini
    else:
        raise ValueError("지원하지 않는 모델 타입입니다: 'minilm' 또는 'gemini'를 사용하세요.")
    
    query_vector_str = str(query_vector)

    # 키워드 like 쿼리 조합
    keywords = [ keyword.strip() for keyword in query_text.strip().split(',') if keyword.strip() ]

    execute_parmas = {
            # query_vector": query_vector_str,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "user_id": user_id
        }


    like_keyword_query = []
    for i, keyword in enumerate(keywords):
        params_key = f'like_{i}'
        execute_parmas[params_key] = f'%{keyword}%'
        like_keyword_query.append ( f' chunks.chunk_text like :{params_key} ')
        # 예시 [ 'chunks.chunk_text like :like_1', 'chunks.chunk_text like :like_2', 'chunks.chunk_text like :like_3' ]


    full_like_query_injection = ' OR '.join(like_keyword_query)
    # 예시 'chunks.chunk_text like :like_1 OR 'chunks.chunk_text like :like_2 OR 'chunks.chunk_text like :like_3 

    # --- 최종 SQL 쿼리 ---
    query = text(f"""
        WITH ranked_chunks AS (
            SELECT
                chunks.chunk_id,
                 chunks.chunk_text,
                chunks.chunk_metadata,
                sources.source_identifier,
                -- 1) 유사도 계산 점수  
                1 - (vectors.embedding_vector <=> '{query_vector_str}' ) AS similarity,
                RANK() OVER (ORDER BY vectors.embedding_vector <=> '{query_vector_str}' ) as rnk,
                case when ( {full_like_query_injection} ) THEN 1 ELSE 0 END AS keyword_match
            FROM
                 llm_agent_rag.{vector_table.__tablename__} AS vectors
            JOIN
                llm_agent_rag.rag_document_chunks AS chunks ON vectors.chunk_id = chunks.chunk_id
            JOIN
                llm_agent_rag.rag_sources AS sources ON chunks.document_id = sources.document_id
            WHERE
                -- 1. 활성화된 문서만 검색 대상으로 함
                sources.is_active = true
                -- 2. 접근 권한 확인:
                AND (
                    -- 2.1. scope 타입이 'global'인 문서는 누구나 접근 가능
                    sources.access_scope ->> 'type' = 'global'
                    -- 2.2. 또는, scope 타입이 'user'이고 user_id가 일치하는 문서
                    OR (
                        sources.access_scope ->> 'type' = 'user'
                        AND sources.access_scope ->> 'user_id' = :user_id
                    )
                )
        )
        SELECT
            chunk_id,
            chunk_text,
            similarity,
            chunk_metadata,
            source_identifier,
            (0.6 * similarity) + (0.4 * keyword_match) AS final_score
        FROM
            ranked_chunks
        WHERE
            similarity >= :similarity_threshold
            OR keyword_match = 1
        ORDER BY
            final_score DESC, similarity DESC
        LIMIT :top_k;
    """)

    top_k = min(top_k,20)

    # 쿼리 실행 시 user_id 파라미터를 추가합니다.
    results = db.execute(
        query,
        execute_parmas
    ).fetchall()

    response = []
    for item in results:
        response.append({
            "text": item.chunk_text,
            "similarity": item.similarity,
            "source_identifier": item.source_identifier ,
        })

    return response



    



    # pgvector의 코사인 유사도 연산자(<=>)를 사용하여 검색 쿼리를 실행합니다.
    # 코사인 거리는 0에 가까울수록 유사하므로, 1을 빼서 '유사도 점수'로 변환합니다 (1에 가까울수록 유사).
    # NOTE: SQLAlchemy 2.0+ 에서는 파라미터 바인딩 시 :param_name 형식을 사용합니다.
    # 벡터를 문자열로 변환하여 쿼리에 직접 넣는 것은 SQL Injection에 취약할 수 있으나,
    # pgvector에서는 list를 직접 바인딩하는 것이 복잡하여 종종 이 방식을 사용합니다.
    # 프로덕션에서는 ORM 레벨에서 지원하는 방식을 우선적으로 고려해야 합니다.

    
pass