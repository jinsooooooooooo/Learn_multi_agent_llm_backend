import uuid
from agents.base_agent import BaseAgent
from core.onspace_api import get_meeting_rooms, reserve_meeting_room, cancel_meeting_room

class MeetingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MeetingAgent",
            role_prompt=(
                "당신은 회사 내부 회의실 예약을 도와주는 AI 비서입니다. "
                "사용자 요청에 따라 회의실 목록을 보여주거나 예약을 진행하세요."
            ),
        )

    def handle(self, session_id:str , user_id: str, model: str, message: str) -> tuple[str, str]:
        """회의실 업무 처리 """

        # 1. seesion_id가 없는 경우 대화 세션 생성
        if session_id is None or session_id.strip() == "":
            # session_id = insert_chat_seession(user_id, self.name, model, title)
            session_id = str(uuid.uuid4()) 
            print(f'[meeting_agent.py] create new seesion_id!!!! -> {session_id}')

        # 2. 이 세션에서 이뤄진 대화 시트로리르저장 한다.
        chat_history = []  
        # fetch_chat_history(seesion_id) from databse


        # 3. model + agent 조합으로 prompt 조합
        # get_prompt(model, self.name) from databse

        rooms = get_meeting_rooms()
        room_info = ", ".join([f"{r['name']}({r['capacity']}명, {'예약가능' if r['available'] else f'예약불가. {r['user']}가 예약중입니다.'})" for r in rooms])
        
        self.role_prompt = f"""{self.role_prompt}\n\n 
        다음은 현재 회의실 목록입니다:
        {room_info}
        
        - 사용자가 단순히 회의실 상태를 물어보면 예약 없이 목록만 정리해 주세요. 
        - 만약 사용자가 회의실과 관계 없는 요청을 했다면 현재 회의시 목록은 굳이 답변하지 않아도 좋습니다. 
        - 사용자가 '예약' 또는 '예약해줘' 등의 의도를 표현하면 적절한 회의실 조건과 시간을 판단하여 추천하고,
          추천한 회의실 이름과 시간을 '###예약:<회의실이름> | <시작시간>~<종료시간>' 형태로 출력해주세요.
          <시작시간>과 <종료시간>의 양식은 <HH24:00> 으로 표현해주세요
          예: "A 회의실이 적합합니다. ###예약:A | 15:00~17:00"
          단, 예약 가능한 회의실만 선택하세요. 
        - 사용자가 '예약취소' 또는 '에약취소해줘' 등의 의도를 표현하면 적절한 회의실 이름을 판단하고,
          회의실 이름을 '###취소:<회의실이름>| <시작시간>~<종료시간>' 형태로 출력해주세요.
          <시작시간>과 <종료시간>의 양식은 <HH24:00> 으로 표현해주세요
          예: "A 회의실이 적합합니다. ###취소:A | 12:00~15:00"
          단, 이미 예약 되어 있는 회의실만 취소 합니다.. 
        """

        # 4. llm 질의하기 
        # save_history(seesion_id,'USER',message)
        llm_reply = self._llm_reply(model, message, chat_history)

        # 5. LLM 답변 히스토리 저장 
        # save_history(seesion_id,'AGENT',llm_reply)

        # 회의실 예약 여부 감지
        if "###예약:" in llm_reply:
            room_name = llm_reply.split("###예약:")[-1].strip().split()[0]
            result = reserve_meeting_room(room_name)
            llm_reply = llm_reply + "\n\n" + result["message"]
        
        # 회의실 취소 여부 감지
        if "###취소:" in llm_reply:
            room_name = llm_reply.split("###취소:")[-1].strip().split()[0]
            result = cancel_meeting_room(room_name)
            llm_reply = llm_reply + "\n\n" + result["message"]
        
        return llm_reply, session_id
