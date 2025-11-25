from backend.agents.base_agent import BaseAgent
from backend.core.rag_engine import get_minilm_embeddings_batch
from backend.database.db_manager import OrmBase
from backend.database.crud import rag_crud
from sqlalchemy.orm import Session



class RagChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RagChatAgent",
            role_prompt=(
                "당신은 사용자의 업무를 도와주는 AI 어시스턴트입니다. "
                "RAG 기반의 문맥이 제공될 테니 이를 참고하여 답변해주세요."
            ),
        )

           


    def handle(self, db: Session, rag_db: Session, session_id:str, user_id:str, model:str, message:str) -> tuple[str,str]:
        
        # seesion_id 컨트롤 다음에 구현 TO-DO
        #   - db.create_session  
        # 메세지 히스토리 컨트롤 다음에 구현 TO-DO
        #   - db.get_messages

        # RAG에서 유사한 문맥을 찾아 시스템 프롬프트에 조합
        rag_document_str = self._rag_documents_serch(rag_db, user_id, message)

        final_system_prompt=f"""
        {self.role_prompt}\n\n
        [지침]:
            - 주어진 RAG 문맥을 기반으로 사용자 요청에 대한 답변을 완성해주세요 
            - 만약 주어진 RAG 문맥을 활용하여 답변을 오나성하였다면, 답변 마지막에 반드시 "[RAG 출처:<출처>]"를 명시해주세요
            - 혹시 주어진 문맥이 없거나 혹은 주어진 문맥과 질의사항이 관계가 없다면, 당신이 알고 있는 최신 정보를 기반으로 답변해주세요 
            
        [문맥]:
        {rag_document_str}         
        """
        
        # 메세지 저장 다음에 구현
        #   - save_message
        
        llm_reply = self._llm_reply(model=model,message=message,chat_history=None,prompt=final_system_prompt)
        
        # 메세지 저장 다음에 구현
        #   - save_message

        return [llm_reply,'def']    

   

    # ----- 입력된 메세지(질의)와 유사한 RAG 데이터 찾기 
    def _rag_documents_serch(self, rag_db:Session, user_id:str, query_text:str ) -> str:
        
        # 문서 임베딩에 사용했던 것과 "반드시 동일한" 모델을 사용해야 합니다.
        # get_minilm_embeddings_batch는 텍스트 '리스트'를 인자로 받으므로,query_text를 리스트에 담아 전달합니다.
        # 결과 또한 벡터 '리스트'이므로, 첫 번째([0) 원소를 가져옵니다.
        query_vector = get_minilm_embeddings_batch([query_text])[0]
        
        retrieved_chunks = rag_crud.search_similar_chunks(
            db=rag_db,
            user_id=user_id,
            query_vector=query_vector,
            model_type='minilm',
            similarity_threshold=0.5

        )
        print(f"총 {len(retrieved_chunks)}개의 관련성 높은 청크를 찾았습니다.")
        rag_documents_str = ''
        for i, chunk in enumerate(retrieved_chunks,start=1):
            print(f"  - 청크 #{i+1} (유사도: {chunk['similarity']:.4f}, 출처: {chunk['source_identifier']}): '{chunk['text'][:80]}...'")
            rag_documents_str = f'{rag_documents_str}   - RAG({i}): {chunk['text']} \n(출처: {chunk['source_identifier']})\n\n'

        return rag_documents_str   
   

        
        
    

        
         