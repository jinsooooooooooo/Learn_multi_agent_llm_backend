import json
from backend.agents.base_agent import BaseAgent
from backend.core.llm_core import call_llm, call_llm_stream
from backend.core.rag_engine import get_minilm_embeddings_batch
from backend.database.db_manager import OrmBase
from backend.database.crud import rag_crud
from sqlalchemy.orm import Session




class RagChatAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RagChatAgent",
            role_prompt=f"""
당신은 사용자의 업무를 도와주는 AI 어시스턴트입니다.
RAG 기반의 문맥이 제공될 테니 이를 참고하여 답변해주세요.           
[지침]:
    - 주어진 RAG 문맥을 기반으로 사용자 요청에 대한 답변을 완성해주세요 
    - 만약 주어진 RAG 문맥을 활용하여 답변을 생성하였다면, 답변 마지막에 반드시 출처를 명시해주세요 예시: (출처: 클래식.txt)
    - 혹시 주어진 문맥이 없거나, 주어진 문맥과 연관됭 정보가 없다면 문멕을 무시하시고 당신이 알고 있는 최신 정보를 기반으로 답변해주세요
 """,
        )

           


    def handle(self, db: Session, chat_id:str, user_id:str, model:str, message:str) -> tuple[str,str]:
        
        try:
            
            last_sequence = 0
            chat_history = []

            # seesion_id 가 없으면 새로운 채팅 세션을 구현
            if chat_id == None or chat_id.strip() == "":
                chat_id = self._create_chat_seesion(db=db, user_id=user_id, agent_id=self.name)
            # seesion_id가 있으면 기존 채팅의 히스토리와 마지막 sequence를 가져온다.
            else:
                chat_history_orm = self._get_chat_history(db=db, chat_id=chat_id)
                for history in chat_history_orm:
                    chat_history.append({
                        'role': history.role,
                        'content': history.content
                    })
                    last_sequence = history.sequence


            # user_massage 저장
            user_sequence = last_sequence + 1
            self._save_massgae_history(db=db, chat_id=chat_id, model_id=model, role='user', content=message, sequence=user_sequence)
            
            # prompot 구성하기 위한
            # --- 1단계: RAG 검색어 생성을 위한 프롬프트 구성 ---
            query_for_rag = f"""
    [이전 대화]
    {self._format_history_to_prompt(chat_history)}
    [최신 질문]
    {message}

    [지침]
    위 '이전 대화'의 맥락 들과 '최신 질문'을 바탕으로 상황을 인지하여, 벡터 데이터베이스에서 정보를 검색하기에 가장 적합한 '핵심 키워드' 생성해 주세요. 다른 설명은 붙이지 말고 오직 '키워드'만 단답으로 생성해 주세요.
    """
            # --- 2단계 : LLM을 호출하여 RAG 검색어 답변 받기
            reply_of_rag = self._llm_reply(model=model,message=query_for_rag,prompt="당신은 사용자와의 대화 이력에서 [최신질문]에 대한 RAG 검색 질의를 찾아내는 Agent 입니다.")

            # print(f'======'*20)
            # print(f'query_for_rag:{query_for_rag}')
            print(f'======'*20)
            print(f'reply_of_rag:{reply_of_rag}')
            print(f'======'*20)


            # --- 3단계: LLM이 생성한 RAG 질의 문장으로  Vector DB 유사한 맥락 가져오기
            rag_document_context = self._rag_documents_serch(db, user_id, reply_of_rag, 0.5)



            # -- 4단계: RAG 맥락을 포함하여 최종 LLM에게 요청할 사용자 질의 완성
            final_user_propt=f"""       
    [문맥]:
    {rag_document_context}   

    [사용자요청]:
    {message} 
            """

            # 최종 사용자 질의 
            llm_reply = self._llm_reply(model=model,message=final_user_propt,chat_history=chat_history,prompt=self.role_prompt)
            
            # assistant 메세지 저장 
            assistant_sequence = user_sequence + 1
            self._save_massgae_history(db=db, chat_id=chat_id, model_id=model, role='assistant', content=llm_reply, sequence=assistant_sequence)
            
            
            # db 변경사항 commit;
            db.commit()

            # 최종 사용자에게 보내지는 답변과 seesion_id 회신
            return [llm_reply,chat_id]    
        
        except Exception as e:
            print(f"RAG Agent 처리 중 에러 발생: {e}")
            db.rollback() # 에러 발생 시 모든 변경사항을 되돌립니다.
            raise e # 에러를 상위로 전파하여 서버 로그에 남깁니다.
            
   
 

    # ----- 입력된 메세지(질의)와 유사한 RAG 데이터 찾기 streming 버전
    async def _handle_stream(self, db: Session, chat_id:str, user_id:str, model:str, message:str) :
        
        try:
            last_sequence = 0
            chat_history = []

            # id 관리 구현예정 :TO-DO
            if chat_id == None or str(chat_id).strip() == "":
                chat_id = self._create_chat_seesion(db,user_id,self.name)
                

            else:
                chat_history_orm = self._get_chat_history(db=db, chat_id=chat_id)
                for history in chat_history_orm:
                    chat_history.append({
                        'role': history.role,
                        'content': history.content
                    })
                    last_sequence = history.sequence
            
            

            # user_massage 저장
            user_sequence = last_sequence + 1
            self._save_massgae_history(db=db, chat_id=chat_id, model_id=model, role='user', content=message, sequence=user_sequence)

            
            # prompot 구성하기 위한
            # --- 1단계: RAG 검색어 생성을 위한 프롬프트 구성 ---
            query_for_rag = f"""
        [이전 대화]
        {self._format_history_to_prompt(chat_history)}
        [최신 질문]
        {message}

        [지침]
        위 '이전 대화'의 맥락 들과 '최신 질문'을 바탕으로 상황을 인지하여, 벡터 데이터베이스에서 정보를 검색하기에 가장 적합한 '핵심 키워드' 생성해 주세요. 다른 설명은 붙이지 말고 오직 '키워드'만 단답으로 생성해 주세요.
        """
            # ---  LLM을 호출하여 RAG 검색어 답변 받기
            reply_of_rag = self._llm_reply(model=model,message=query_for_rag,prompt="당신은 사용자와의 대화 이력에서 [최신질문]에 대한 RAG 검색 질의를 찾아내는 Agent 입니다.")

            print(f'======'*20)
            print(f'reply_of_rag:{reply_of_rag}')

            # ---  LLM이 생성한 RAG 질의 문장으로  Vector DB 유사한 맥락 가져오기
            rag_document_context = self._rag_documents_serch(db, user_id, reply_of_rag, 0.5)

            # 프롬프트 수정 구현예정 :TO-DO 
            # save_massage 구현 예쩡:TO-DO
            final_prompt = f"""
    [문맥]:
    {rag_document_context}

    [사용자요청]: {message}
            """

            metadata_chunk = {
                "type": "chat_id",
                "chat_id": str(chat_id)
               
            }
            yield json.dumps(metadata_chunk) + "\n"
            
            llm_reply = ''
            async for reply_chunk in call_llm_stream(
                model=model,
                prompt=self.role_prompt,
                message=final_prompt,
                chat_history=chat_history
            ):
                if reply_chunk:
                    llm_reply = llm_reply + reply_chunk
                    # yield data
                    # fornte에서 일관성있게 받을 수 있도록 모든 데이터의 테입을 json으로 지정한다.
                    reply_chunk = {
                        "type": "text",
                        "text": str(reply_chunk)
                    }
                    yield json.dumps(reply_chunk, ensure_ascii=False) + "\n"
                    
                
            
            
            # assis_meesage 저장 
            assistant_sequence = user_sequence + 1
            self._save_massgae_history(db=db, chat_id=chat_id, model_id=model, role='assistant', content=llm_reply, sequence=assistant_sequence)
            
            # db 변경사항 commit;
            db.commit()

        except Exception as e:
            print(f"RAG Agent 처리 중 에러 발생: {e}")
            db.rollback() # 에러 발생 시 모든 변경사항을 되돌립니다.
            error_chunk = {
                "type": "error",
                "error": str(e)
            }
            yield json.dumps(error_chunk) + "\n"
            
            raise e # 에러를 상위로 전파하여 서버 로그에 남깁니다.    


        
    











    # ----- 입력된 메세지(질의)와 유사한 RAG 데이터 찾기 
    def _rag_documents_serch(self, db:Session, user_id:str, query_text:str, similarity_threshold: float = 0.5 ) -> str:
        
        # 문서 임베딩에 사용했던 것과 "반드시 동일한" 모델을 사용해야 합니다.
        # get_minilm_embeddings_batch는 텍스트 '리스트'를 인자로 받으므로,query_text를 리스트에 담아 전달합니다.
        # 결과 또한 벡터 '리스트'이므로, 첫 번째([0) 원소를 가져옵니다.
        query_vector = get_minilm_embeddings_batch([query_text])[0]
        
        retrieved_chunks = rag_crud.search_similar_chunks(
            db=db,
            user_id=user_id,
            query_text=query_text,
            query_vector=query_vector,
            model_type='minilm',
            similarity_threshold=similarity_threshold

        )
        print(f"총 {len(retrieved_chunks)}개의 관련성 높은 청크를 찾았습니다.")
        rag_documents_str = ''
        for i, chunk in enumerate(retrieved_chunks,start=1):
            print(f"  - 청크 #{i+1} (유사도: {chunk['similarity']:.4f}, 출처: {chunk['source_identifier']}): '{chunk['text'][:80]}...'")
            rag_documents_str = f'{rag_documents_str}   - RAG({i}): {chunk['text']} \n(출처: {chunk['source_identifier']})\n\n'

        return rag_documents_str   
    

    def _format_history_to_prompt(self, chat_history:list) -> str :
        
        history_prompt:str = ''
        if chat_history == None:
            return ''
        for hist in chat_history:
            history_prompt = f"{history_prompt} - [{hist["role"]}: {hist["content"]}\n"
        return history_prompt



        
         