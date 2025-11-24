import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

# --- 1. 우리가 만든 모듈과 모델 import ---
from backend.core.ncp_storage import ncp_storage_client
from backend.database.crud.rag_crud import get_all_sources, bulk_insert_chunks_and_vectors
from backend.database.models.rag_model import RagSources
# (아직 만들지 않았지만) 앞으로 만들 임베딩 모듈
# from .rag_embedder import get_minilm_embeddings_batch, get_gemini_embeddings_batch

# --- 임시 임베딩 함수 (테스트용) ---
# TODO: 나중에 이 함수들을 rag_embedder.py로 옮기고 실제 구현으로 대체해야 합니다.
def get_minilm_embeddings_batch(texts: list[str]) -> list[list[float]]:
    print(f"임시 MiniLM 임베딩 생성: {len(texts)}개 청크")
    # 실제로는 sentence-transformers 모델로 벡터 생성
    return [[0.1] * 384 for _ in texts] # 384차원의 가짜 벡터

def get_gemini_embeddings_batch(texts: list[str]) -> list[list[float]]:
    print(f"임시 Gemini 임베딩 생성: {len(texts)}개 청크")
    # 실제로는 Google AI API로 벡터 생성
    return [[0.2] * 768 for _ in texts] # 768차원의 가짜 벡터


def _process_single_file(db: Session, file_metadata: dict):
    """하나의 파일을 다운로드, 처리하고 DB에 저장하는 내부 함수"""
    file_key = file_metadata['Key']
    print(f"'{file_key}' 파일 처리 시작...")

    # --- 1. 파일 다운로드 ---
    file_content_bytes = ncp_storage_client.download_file(file_key)
    if not file_content_bytes:
        print(f"'{file_key}' 파일 다운로드 실패.")
        return

    # TODO: 나중에 파일 타입에 따라 다른 Document Loader를 사용해야 합니다.
    # 지금은 모든 파일을 utf-8 텍스트로 가정합니다.
    try:
        file_text = file_content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        print(f"'{file_key}'은 텍스트 파일이 아닙니다. 건너뜁니다.")
        return

    # --- 2. 텍스트 분할 (Chunking) ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_text(file_text)
    print(f"'{file_key}' 파일을 {len(chunks)}개의 청크로 분할했습니다.")

    # --- 3. 임베딩 생성 ---
    minilm_vectors = get_minilm_embeddings_batch(chunks)
    gemini_vectors = get_gemini_embeddings_batch(chunks)

    # --- 4. DB 저장을 위한 데이터 구조 조립 ---
    chunks_data = []
    for i, (text, vec_minilm, vec_gemini) in enumerate(zip(chunks, minilm_vectors, gemini_vectors)):
        chunks_data.append({
            "text": text,
            "sequence": i,
            "metadata": {"source_file": file_key},
            "vector_minilm": vec_minilm,
            "vector_gemini": vec_gemini,
        })
    
    # --- 5. DB에 저장 ---
    # RagSources 객체 생성
    new_source = RagSources(
        source_type=file_key.split('.')[-1], # 확장자 추출
        source_identifier=file_key,
        last_modified_time=file_metadata['LastModified'],
        file_size=file_metadata['Size'],
        access_scope={"type": "global"} # 기본값은 전역 공개
    )
    # CRUD 함수를 사용하여 Bulk Insert 실행
    bulk_insert_chunks_and_vectors(db, new_source, chunks_data)
    print(f"'{file_key}' 파일 처리 완료 및 DB 저장 성공.")


def refresh_rag_data(db: Session):
    """
    NCP Object Storage와 RAG DB를 동기화하는 메인 함수.
    """
    print("RAG 데이터 동기화 프로세스를 시작합니다...")
    # 1. NCP 버킷의 모든 파일 목록 가져오기
    ncp_files = ncp_storage_client.list_files()
    if not ncp_files:
        print("NCP 버킷에 파일이 없거나 조회에 실패했습니다.")
        return

    # 2. 현재 DB에 저장된 모든 소스 정보 가져오기
    db_sources_list = get_all_sources(db)
    # 빠른 조회를 위해 딕셔너리로 변환: {'file/path.txt': RagSources_객체}
    db_sources_map = {source.source_identifier: source for source in db_sources_list}
    
    print(f"NCP 버킷에서 {len(ncp_files)}개의 파일을, DB에서 {len(db_sources_map)}개의 소스를 찾았습니다.")

    # 3. NCP 파일 목록을 순회하며 DB와 비교
    for file_meta in ncp_files:
        file_key = file_meta['Key']
        
        # 만약 파일이 폴더라면 건너뛰기
        if file_key.endswith('/'):
            continue

        db_record = db_sources_map.get(file_key)

        # 경우 1: DB에 없는 새로운 파일
        if not db_record:
            print(f"[신규] 새로운 파일 '{file_key}'을(를) 발견했습니다.")
            _process_single_file(db, file_meta)
        
        # 경우 2: DB에 있지만, 수정 시간이나 파일 크기가 변경된 파일
        elif db_record.last_modified_time != file_meta['LastModified' or db_record.file_size != file_meta['Size']]:
            print(f"[변경] '{file_key}' 파일이 변경되었습니다.")
            # TODO: 기존 문서를 is_active=False로 바꾸고, 새로 처리하는 로직 추가 필요
            # 지금은 단순화를 위해 그냥 새로 추가 처리합니다.
            _process_single_file(db, file_meta)

        # 경우 3: DB에도 있고, 변경되지도 않은 파일 -> 아무것도 안 함
        else:
            print(f"[유지] '{file_key}' 파일은 최신 상태입니다.")
            pass
    
    # TODO: NCP에는 없는데 DB에만 있는 파일(삭제된 파일)을 찾아 is_active=False로 처리하는 로직 추가 필요

    db.commit() # 모든 변경사항을 최종 커밋
    print("RAG 데이터 동기화 프로세스를 완료했습니다.")