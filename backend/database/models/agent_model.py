from backend.database.db_manager import OrmBase
from sqlalchemy import Column, ForeignKey, String, Text, Integer, Numeric, Boolean, UUID, JSON, and_
from sqlalchemy.orm import relationship


class LlmModel(OrmBase):
    __tablename__="llm_model"
    __table_args__ = {'schema': 'llm_agent'}

    model_id = Column(String(50), primary_key=True )
    vendor = Column(String(50), nullable=False)
    description = Column(Text)
    max_tokens = Column(Integer)
    input_cost = Column(Numeric(10, 8),)
    output_cost = Column(Numeric(10, 8),)
    is_active = Column(Boolean)


class AgentInfo(OrmBase):
    __tablename__ = 'agent_info'
    __table_args__ = {'schema': 'llm_agent'}

    agent_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    role_description = Column(Text, nullable=False)
    default_tool_chain = Column(Text)
    is_active = Column(Boolean, default=True)
    mode = Column(String(20), nullable=False, default='chat')


class ModelAgentPromptDef(OrmBase):
    __tablename__ = 'model_agent_prompt_def'
    __table_args__ = {'schema': 'llm_agent'}

    config_id = Column(UUID(as_uuid=True), primary_key=True)
    agent_id = Column(String(50), ForeignKey('llm_agent.agent_info.agent_id'), nullable=False) # ForeignKey 제약 조건은 생략 가능
    model_id = Column(String(50), ForeignKey('llm_agent.llm_model.model_id'), nullable=False) # (ORM 관계 설정으로 대체)
    system_prompt_override = Column(Text)
    model_params = Column(JSON)

    agent = relationship(
        "AgentInfo",
        primaryjoin = "and_(ModelAgentPromptDef.agent_id == AgentInfo.agent_id, AgentInfo.AgentInfo == True )"
    )

    model = relationship(
        "LlmModel",
        primaryjoin="and_ ModelAgentPromptDef.model_id == LlmModel.model_id, LlmModel.is_active == True )"
    )
    



