"""
핵심 컴포넌트: 에이전트 상태 관리 및 도구 시스템
"""
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import BaseTool

class AgentState(TypedDict):
    """에이전트 상태를 나타내는 데이터 구조"""
    # add_messages는 상태가 업데이트될 때 메시지를 "추가"하라고 지시합니다.
    # 기본값은 덮어쓰기입니다.
    messages: Annotated[Sequence[BaseMessage], add_messages]

class ToolManager:
    """도구 관리 클래스"""
    
    def __init__(self, retriever):
        self.retriever = retriever
        self.tools = self._create_tools()
    
    def _create_tools(self) -> list[BaseTool]:
        """검색 도구를 생성합니다."""
        retriever_tool = create_retriever_tool(
            self.retriever,
            "retrieve_financial_info",
            "네이버, 야후, 다음의 금융 관련 정보를 검색하고 반환합니다. "
            "사용자의 질문과 관련된 금융 정보를 찾을 때 사용하세요.",
        )
        
        return [retriever_tool]
    
    def get_tools(self) -> list[BaseTool]:
        """사용 가능한 도구 목록을 반환합니다."""
        return self.tools
    
    def get_tool_names(self) -> list[str]:
        """도구 이름 목록을 반환합니다."""
        return [tool.name for tool in self.tools]

def create_tools_condition(state) -> str:
    """
    에이전트가 도구를 사용할지 결정하는 조건부 함수
    
    Args:
        state: 현재 에이전트 상태
        
    Returns:
        str: "tools" 또는 END
    """
    messages = state["messages"]
    
    # 마지막 메시지가 도구 호출을 요청하는지 확인
    last_message = messages[-1]
    
    # 도구 사용이 필요한 경우 "tools" 반환
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # 도구 사용이 필요하지 않은 경우 END 반환
    return "end"

def validate_state(state: AgentState) -> bool:
    """
    에이전트 상태의 유효성을 검증합니다.
    
    Args:
        state: 검증할 상태
        
    Returns:
        bool: 유효한 상태인지 여부
    """
    if not isinstance(state, dict):
        return False
    
    if "messages" not in state:
        return False
    
    if not isinstance(state["messages"], (list, tuple)):
        return False
    
    return True

def get_last_user_message(state: AgentState) -> str:
    """
    상태에서 마지막 사용자 메시지를 추출합니다.
    
    Args:
        state: 에이전트 상태
        
    Returns:
        str: 마지막 사용자 메시지
    """
    if not validate_state(state):
        raise ValueError("유효하지 않은 상태입니다.")
    
    messages = state["messages"]
    
    # 사용자 메시지를 찾습니다 (HumanMessage)
    for message in reversed(messages):
        if hasattr(message, 'type') and message.type == 'human':
            return message.content
    
    # 사용자 메시지를 찾을 수 없는 경우
    raise ValueError("사용자 메시지를 찾을 수 없습니다.")

def get_last_assistant_message(state: AgentState) -> str:
    """
    상태에서 마지막 어시스턴트 메시지를 추출합니다.
    
    Args:
        state: 에이전트 상태
        
    Returns:
        str: 마지막 어시스턴트 메시지
    """
    if not validate_state(state):
        raise ValueError("유효하지 않은 상태입니다.")
    
    messages = state["messages"]
    
    # 어시스턴트 메시지를 찾습니다 (AIMessage)
    for message in reversed(messages):
        if hasattr(message, 'type') and message.type == 'ai':
            return message.content
    
    # 어시스턴트 메시지를 찾을 수 없는 경우
    raise ValueError("어시스턴트 메시지를 찾을 수 없습니다.")
