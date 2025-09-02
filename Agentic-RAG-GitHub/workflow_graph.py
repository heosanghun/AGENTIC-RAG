"""
워크플로우 그래프: LangGraph를 사용한 Agentic RAG 워크플로우 구성
"""
import logging
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from components import AgentState, ToolManager, create_tools_condition
from workflow_nodes import agent, grade_documents, rewrite, generate
from data_pipeline import DataPipeline

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticRAGWorkflow:
    """Agentic RAG 워크플로우 클래스"""
    
    def __init__(self, data_pipeline: DataPipeline = None):
        self.data_pipeline = data_pipeline
        self.tool_manager = None
        self.workflow = None
        self.graph = None
        
        if data_pipeline:
            self._initialize_tools()
    
    def _initialize_tools(self):
        """도구를 초기화합니다."""
        if self.data_pipeline:
            retriever = self.data_pipeline.get_retriever()
            self.tool_manager = ToolManager(retriever)
            logger.info("도구 초기화 완료")
    
    def build_workflow(self) -> 'AgenticRAGWorkflow':
        """워크플로우를 구축합니다."""
        logger.info("워크플로우 구축 시작")
        
        try:
            # 워크플로우를 정의합니다.
            self.workflow = StateGraph(AgentState)
            
            # 순환할 노드들을 정의합니다.
            self.workflow.add_node("agent", agent)  # 에이전트 노드
            
            # 검색 도구 노드 (ToolNode 사용)
            if self.tool_manager:
                retrieve = ToolNode(self.tool_manager.get_tools())
            else:
                # 도구가 없는 경우 임시 노드 생성
                retrieve = self._create_temp_retrieve_node()
            
            self.workflow.add_node("retrieve", retrieve)  # 검색 도구 노드
            self.workflow.add_node("rewrite", rewrite)    # 질문 재작성 노드
            self.workflow.add_node("generate", generate)  # 답변 생성 노드
            
            # 엣지(Edge) 및 조건부 엣지(Conditional Edge) 설정
            self._setup_edges()
            
            # 그래프 컴파일
            self.graph = self.workflow.compile()
            
            logger.info("워크플로우 구축 완료")
            return self
            
        except Exception as e:
            logger.error(f"워크플로우 구축 실패: {str(e)}")
            raise
    
    def _create_temp_retrieve_node(self):
        """임시 검색 노드를 생성합니다."""
        def temp_retrieve(state):
            logger.info("---임시 검색 노드 실행---")
            # 실제 검색 대신 더미 데이터 반환
            from langchain_core.messages import AIMessage
            dummy_content = "임시 검색 결과: 금융 정보에 대한 기본 데이터입니다."
            return {"messages": [AIMessage(content=dummy_content)]}
        
        return temp_retrieve
    
    def _setup_edges(self):
        """워크플로우의 엣지를 설정합니다."""
        # 에이전트 노드를 호출하여 검색을 결정합니다.
        self.workflow.add_edge(START, "agent")
        
        # 검색 여부를 결정합니다.
        self.workflow.add_conditional_edges(
            "agent",
            # 에이전트 결정 평가
            create_tools_condition,
            {
                # 조건 출력을 그래프 내 노드로 변환, 반환 값: 실행 노드
                "tools": "retrieve",
                "end": END,
            },
        )
        
        # 검색 후 문서 관련성 평가
        self.workflow.add_conditional_edges(
            "retrieve",
            # 문서 관련성 평가
            grade_documents,
            {
                # 조건 출력을 그래프 내 노드로 변환, 반환 값: 실행 노드
                "generate": "generate",
                "rewrite": "rewrite",
            },
        )
        
        # 최종 엣지 설정
        self.workflow.add_edge("generate", END)
        self.workflow.add_edge("rewrite", "agent")  # 재작성 후 에이전트로 돌아감
    
    def get_graph(self):
        """컴파일된 그래프를 반환합니다."""
        if self.graph is None:
            raise ValueError("그래프가 컴파일되지 않았습니다. build_workflow()을 먼저 실행하세요.")
        return self.graph
    
    def visualize_graph(self):
        """그래프를 시각화합니다."""
        try:
            graph = self.get_graph()
            # Mermaid 다이어그램 생성
            mermaid_diagram = graph.get_graph(xray=True).draw_mermaid()
            logger.info("Mermaid 다이어그램 생성 완료")
            return mermaid_diagram
        except Exception as e:
            logger.error(f"그래프 시각화 실패: {str(e)}")
            return None
    
    def run_workflow(self, question: str):
        """워크플로우를 실행합니다."""
        try:
            from langchain_core.messages import HumanMessage
            
            # 입력 준비
            inputs = {
                "messages": [
                    HumanMessage(content=question),
                ]
            }
            
            logger.info(f"워크플로우 실행 시작: {question}")
            
            # 그래프 실행
            graph = self.get_graph()
            results = []
            
            for output in graph.stream(inputs):
                for key, value in output.items():
                    logger.info(f"노드 '{key}'의 출력 결과:")
                    logger.info(f"  {value}")
                    results.append((key, value))
            
            logger.info("워크플로우 실행 완료")
            return results
            
        except Exception as e:
            logger.error(f"워크플로우 실행 실패: {str(e)}")
            raise

def create_workflow_with_data_pipeline() -> AgenticRAGWorkflow:
    """데이터 파이프라인과 함께 워크플로우를 생성합니다."""
    try:
        # 데이터 파이프라인 구축
        logger.info("데이터 파이프라인 구축 시작")
        data_pipeline = DataPipeline()
        data_pipeline.build_pipeline()
        logger.info("데이터 파이프라인 구축 완료")
        
        # 워크플로우 생성
        workflow = AgenticRAGWorkflow(data_pipeline)
        workflow.build_workflow()
        
        return workflow
        
    except Exception as e:
        logger.error(f"워크플로우 생성 실패: {str(e)}")
        raise

def main():
    """메인 실행 함수"""
    try:
        # 워크플로우 생성
        workflow = create_workflow_with_data_pipeline()
        
        # 그래프 시각화
        mermaid_diagram = workflow.visualize_graph()
        if mermaid_diagram:
            print("워크플로우 구조:")
            print(mermaid_diagram)
        
        # 테스트 실행
        test_question = "agentic rag가 어떤 의미야?"
        print(f"\n테스트 질문: {test_question}")
        
        results = workflow.run_workflow(test_question)
        
        print("\n실행 결과:")
        for node_name, result in results:
            print(f"\n{node_name}: {result}")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
