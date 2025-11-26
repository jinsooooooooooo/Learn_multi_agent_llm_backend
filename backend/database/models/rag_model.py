from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

# 중요! RAG 모델들은 새로운 RAG DB에 매핑되므로,
# 별도의 Base를 사용하거나 기존 Base를 사용하되 engine 바인딩을 명확히 해야 합니다.
# 여기서는 단순화를 위해 기존 OrmBase를 함께 사용합니다.
from backend.database.db_manager import OrmBase

# --- 공통 메타데이터 테이블 ---
class RagSources(OrmBase):
    __tablename__ = 'rag_sources'
    __table_args__ = {'schema': 'llm_agent_rag'}

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False)
    source_identifier = Column(String(255), nullable=False, unique=True)
    last_modified_time = Column(DateTime(timezone=True))
    file_size = Column(Integer)
    is_active = Column(Boolean, default=True, nullable=False)
    access_scope = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 테이블간 relationship 선언
    chunks = relationship(
        "RagDocumentChunks",
        primaryjoin="RagSources.document_id == RagDocumentChunks.document_id",
        cascade="all, delete-orphan",
        back_populates="source"

    )

# --- 공통 청크 정보 (문서 ID, 텍스트, 메타데이터 등) ---
class RagDocumentChunks(OrmBase):
    __tablename__ = 'rag_document_chunks'
    __table_args__ = {'schema': 'llm_agent_rag'}

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('llm_agent_rag.rag_sources.document_id'), nullable=False)
    chunk_text = Column(Text, nullable=False)
    sequence_num = Column(Integer, nullable=False)
    chunk_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 테이블간 relationship 선언
    source = relationship("RagSources", back_populates="chunks")
    vector_minilm = relationship("RagVectorsMinilm", uselist=False, back_populates="chunk", cascade="all, delete-orphan")
    vector_gemini = relationship("RagVectorsGemini", uselist=False, back_populates="chunk", cascade="all, delete-orphan")



# --- 모델별 벡터 테이블 ---
class RagVectorsMinilm(OrmBase):
    __tablename__ = 'rag_vectors_minilm'
    __table_args__ = {'schema': 'llm_agent_rag'}

    # chunk_id를 PK이자 FK로 사용하여 Chunks 테이블과 1:1 관계를 맺습니다.
    chunk_id = Column(UUID(as_uuid=True), ForeignKey('llm_agent_rag.rag_document_chunks.chunk_id'), primary_key=True )
    embedding_vector = Column(Vector(384))

    # 테이블간 relationship 선언
    chunk = relationship(
        "RagDocumentChunks",
        uselist=False,
        primaryjoin="RagVectorsMinilm.chunk_id == RagDocumentChunks.chunk_id",
        back_populates="vector_minilm"
    )
    

class RagVectorsGemini(OrmBase):
    __tablename__ = 'rag_vectors_gemini'
    __table_args__ = {'schema': 'llm_agent_rag'}

    chunk_id = Column(UUID(as_uuid=True), ForeignKey('llm_agent_rag.rag_document_chunks.chunk_id'), primary_key=True)
    embedding_vector = Column(Vector(768))

    # 테이블간 relationship 선언
    chunk = relationship(
        "RagDocumentChunks",
        uselist=False,
        primaryjoin="RagVectorsGemini.chunk_id == RagDocumentChunks.chunk_id",
        back_populates="vector_gemini"
    )