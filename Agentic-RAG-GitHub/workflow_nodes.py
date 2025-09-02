"""
워크플로우 노드: 각 단계별 처리 로직 구현
"""
import logging
from typing import Literal
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from components import AgentState, get_last_user_message, get_last_assistant_message
from config import OPENAI_MODEL, TEMPERATURE

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def agent(state: AgentState) -> dict:
    """
    에이전트 노드: 사용자의 질문에 따라 도구를 호출하여 검색을 수행합니다.
    
    Args:
        state: 현재 에이전트 상태
        
    Returns:
        dict: 메시지에 에이전트 응답이 추가된 업데이트된 상태
    """
    logger.info("---에이전트 호출---")
    
    try:
        from components import ToolManager
        
        # ToolManager는 외부에서 주입되어야 합니다
        # 여기서는 임시로 생성 (실제로는 워크플로우에서 주입)
        messages = state["messages"]
        
        model = ChatOpenAI(
            temperature=TEMPERATURE, 
            streaming=True, 
            model=OPENAI_MODEL
        )
        
        # 도구 바인딩 (실제로는 ToolManager에서 가져와야 함)
        # model = model.bind_tools(tools)
        
        response = model.invoke(messages)
        
        # 응답을 상태에 추가
        return {"messages": [response]}
        
    except Exception as e:
        logger.error(f"에이전트 실행 중 오류: {str(e)}")
        error_message = AIMessage(content=f"에이전트 실행 중 오류가 발생했습니다: {str(e)}")
        return {"messages": [error_message]}

def grade_documents(state: AgentState) -> Literal["generate", "rewrite"]:
    """
    문서 관련성 평가 노드: 검색된 문서가 질문과 관련이 있는지 평가합니다.
    
    Args:
        state: 현재 상태
        
    Returns:
        str: 문서의 관련성에 따라 다음 노드 결정 ("generate" 또는 "rewrite")
    """
    logger.info("---문서 관련성 평가---")
    
    try:
        # 데이터 모델 정의
        class Grade(BaseModel):
            """관련성 평가를 위한 이진 점수."""
            binary_score: str = Field(
                description="관련성 점수 'yes' 또는 'no'",
                enum=["yes", "no"]
            )
        
        # LLM 모델 정의
        model = ChatOpenAI(
            temperature=0, 
            model=OPENAI_MODEL, 
            streaming=True
        )
        
        # LLM에 데이터 모델 적용
        llm_with_tool = model.with_structured_output(Grade)
        
        prompt = PromptTemplate(
            template="""당신은 사용자 질문에 대한 검색된 문서의 관련성을 평가하는 평가자입니다.
            
            여기 검색된 문서가 있습니다: 
            {context}
            
            여기 사용자 질문이 있습니다: {question}
            
            문서가 사용자 질문과 관련된 키워드 또는 의미를 포함하면 관련성이 있다고 평가하세요.
            문서가 질문과 관련이 있는지 여부를 나타내기 위해 'yes' 또는 'no'로 이진 점수를 주세요.
            
            평가 기준:
            - 'yes': 문서가 질문과 직접적으로 관련된 정보를 포함
            - 'no': 문서가 질문과 관련이 없거나 매우 낮은 관련성
            
            답변:""",
            input_variables=["context", "question"],
        )
        
        messages = state["messages"]
        question = get_last_user_message(state)
        
        # 마지막 메시지에서 검색된 문서 추출
        last_message = messages[-1]
        docs = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # 관련성 평가 실행
        scored_result = llm_with_tool.invoke({
            "question": question, 
            "context": docs
        })
        
        score = scored_result.binary_score
        
        if score == "yes":
            logger.info("---결정: 문서 관련성 있음---")
            return "generate"
        else:
            logger.info("---결정: 문서 관련성 없음---")
            return "rewrite"
            
    except Exception as e:
        logger.error(f"문서 관련성 평가 중 오류: {str(e)}")
        # 오류 발생 시 기본적으로 rewrite로 진행
        return "rewrite"

def rewrite(state: AgentState) -> dict:
    """
    질문 재작성 노드: 검색된 문서의 관련성이 낮을 때, 
    더 나은 검색 결과를 위해 질문을 재작성합니다.
    
    Args:
        state: 현재 상태
    
    Returns:
        dict: 재구성된 질문으로 업데이트된 상태
    """
    logger.info("---질문 변형---")
    
    try:
        question = get_last_user_message(state)
        
        msg = [
            HumanMessage(
                content=f"""다음 입력을 보고 근본적인 의도나 의미를 파악해보세요.
                초기 질문은 다음과 같습니다:
                
                -------
                {question}
                -------
                
                개선된 질문을 만들어주세요. 다음을 고려하세요:
                1. 더 구체적이고 명확한 표현
                2. 관련 키워드 추가
                3. 검색 가능한 형태로 변환
                4. 원래 의도 유지
                
                개선된 질문:"""
            )
        ]
        
        # 질문 재작성 실행
        model = ChatOpenAI(
            temperature=0, 
            model=OPENAI_MODEL, 
            streaming=True
        )
        response = model.invoke(msg)
        
        return {"messages": [response]}
        
    except Exception as e:
        logger.error(f"질문 재작성 중 오류: {str(e)}")
        error_message = AIMessage(content=f"질문 재작성 중 오류가 발생했습니다: {str(e)}")
        return {"messages": [error_message]}

def generate(state: AgentState) -> dict:
    """
    답변 생성 노드: 관련성 높은 문서를 기반으로 최종 답변을 생성합니다.
    
    Args:
        state: 현재 상태
    
    Returns:
        dict: 생성된 답변으로 업데이트된 상태
    """
    logger.info("---생성---")
    
    try:
        question = get_last_user_message(state)
        
        # 마지막 메시지에서 검색된 문서 추출
        messages = state["messages"]
        last_message = messages[-1]
        docs = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # 프롬프트 정의
        template = """당신은 질문-답변 작업을 위한 어시스턴트입니다.
        아래 제공된 문맥을 사용하여 질문에 답변해주세요.
        
        답을 모를 경우 '모르겠습니다'라고 말해주세요. 
        답변은 최대 3문장으로 간결하게 작성하세요.
        
        질문: {question}
        문맥: {context}
        
        답변:"""
        
        prompt = PromptTemplate(
            template=template, 
            input_variables=["context", "question"]
        )
        
        # LLM
        llm = ChatOpenAI(
            model_name=OPENAI_MODEL, 
            temperature=0, 
            streaming=True
        )
        
        # 체인
        rag_chain = prompt | llm | StrOutputParser()
        
        # 실행
        response = rag_chain.invoke({
            "context": docs, 
            "question": question
        })
        
        return {"messages": [AIMessage(content=response)]}
        
    except Exception as e:
        logger.error(f"답변 생성 중 오류: {str(e)}")
        error_message = AIMessage(content=f"답변 생성 중 오류가 발생했습니다: {str(e)}")
        return {"messages": [error_message]}

def create_error_handler(error_message: str = "처리 중 오류가 발생했습니다."):
    """
    오류 처리를 위한 핸들러 함수를 생성합니다.
    
    Args:
        error_message: 오류 메시지
        
    Returns:
        function: 오류 처리 함수
    """
    def error_handler(state: AgentState) -> dict:
        logger.error(f"워크플로우 오류: {error_message}")
        error_response = AIMessage(content=error_message)
        return {"messages": [error_response]}
    
    return error_handler
