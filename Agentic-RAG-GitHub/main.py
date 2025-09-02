"""
Agentic RAG 지능형 정보 검색 시스템 - 메인 실행 파일
"""
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import OPENAI_API_KEY
from data_pipeline import DataPipeline
from workflow_graph import AgenticRAGWorkflow, create_workflow_with_data_pipeline

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agentic_rag.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """환경 설정을 확인하고 초기화합니다."""
    logger.info("환경 설정 확인 중...")
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API 키가 설정되지 않았습니다.")
        logger.info("env_example.txt 파일을 .env로 복사하고 API 키를 설정하세요.")
        return False
    
    logger.info("환경 설정 완료")
    return True

def build_data_pipeline():
    """데이터 파이프라인을 구축합니다."""
    logger.info("데이터 파이프라인 구축 시작...")
    
    try:
        pipeline = DataPipeline()
        pipeline.build_pipeline()
        logger.info("데이터 파이프라인 구축 완료")
        return pipeline
    except Exception as e:
        logger.error(f"데이터 파이프라인 구축 실패: {str(e)}")
        return None

def create_workflow(pipeline):
    """워크플로우를 생성합니다."""
    logger.info("워크플로우 생성 시작...")
    
    try:
        workflow = AgenticRAGWorkflow(pipeline)
        workflow.build_workflow()
        logger.info("워크플로우 생성 완료")
        return workflow
    except Exception as e:
        logger.error(f"워크플로우 생성 실패: {str(e)}")
        return None

def test_workflow(workflow):
    """워크플로우를 테스트합니다."""
    logger.info("워크플로우 테스트 시작...")
    
    test_questions = [
        "agentic rag가 어떤 의미야?",
        "금융 시장의 최신 동향은?",
        "투자 포트폴리오 구성 방법은?",
        "주식 시장 분석 방법은?"
    ]
    
    results = {}
    
    for question in test_questions:
        logger.info(f"\n테스트 질문: {question}")
        try:
            result = workflow.run_workflow(question)
            results[question] = result
            logger.info(f"질문 '{question}' 처리 완료")
        except Exception as e:
            logger.error(f"질문 '{question}' 처리 실패: {str(e)}")
            results[question] = f"오류: {str(e)}"
    
    return results

def interactive_mode(workflow):
    """대화형 모드로 워크플로우를 실행합니다."""
    logger.info("대화형 모드 시작 (종료하려면 'quit' 또는 'exit' 입력)")
    
    while True:
        try:
            question = input("\n질문을 입력하세요: ").strip()
            
            if question.lower() in ['quit', 'exit', '종료']:
                logger.info("대화형 모드 종료")
                break
            
            if not question:
                continue
            
            logger.info(f"질문 처리 중: {question}")
            result = workflow.run_workflow(question)
            
            print(f"\n답변: {result}")
            
        except KeyboardInterrupt:
            logger.info("\n사용자에 의해 중단됨")
            break
        except Exception as e:
            logger.error(f"질문 처리 중 오류: {str(e)}")
            print(f"오류가 발생했습니다: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("Agentic RAG 지능형 정보 검색 시스템 시작")
    logger.info("=" * 60)
    
    try:
        # 1. 환경 설정 확인
        if not setup_environment():
            return
        
        # 2. 데이터 파이프라인 구축
        pipeline = build_data_pipeline()
        if not pipeline:
            logger.error("데이터 파이프라인 구축 실패로 시스템을 종료합니다.")
            return
        
        # 3. 워크플로우 생성
        workflow = create_workflow(pipeline)
        if not workflow:
            logger.error("워크플로우 생성 실패로 시스템을 종료합니다.")
            return
        
        # 4. 그래프 시각화
        try:
            mermaid_diagram = workflow.visualize_graph()
            if mermaid_diagram:
                logger.info("워크플로우 구조:")
                logger.info(mermaid_diagram)
        except Exception as e:
            logger.warning(f"그래프 시각화 실패: {str(e)}")
        
        # 5. 사용자 선택
        print("\n실행 모드를 선택하세요:")
        print("1. 자동 테스트 실행")
        print("2. 대화형 모드")
        print("3. 종료")
        
        while True:
            choice = input("\n선택 (1-3): ").strip()
            
            if choice == "1":
                logger.info("자동 테스트 모드 시작")
                results = test_workflow(workflow)
                
                print("\n" + "="*50)
                print("테스트 결과 요약")
                print("="*50)
                for question, result in results.items():
                    print(f"\n질문: {question}")
                    print(f"결과: {result}")
                
                break
                
            elif choice == "2":
                logger.info("대화형 모드 시작")
                interactive_mode(workflow)
                break
                
            elif choice == "3":
                logger.info("시스템 종료")
                break
                
            else:
                print("잘못된 선택입니다. 1, 2, 또는 3을 입력하세요.")
        
        logger.info("=" * 60)
        logger.info("Agentic RAG 시스템 종료")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"시스템 실행 중 치명적 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
