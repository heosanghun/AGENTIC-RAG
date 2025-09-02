"""
시스템 테스트 파일
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

def test_imports():
    """모든 모듈이 정상적으로 import되는지 테스트합니다."""
    print("=== 모듈 Import 테스트 ===")
    
    try:
        from config import OPENAI_API_KEY, OPENAI_MODEL
        print(f"✅ config 모듈 import 성공")
        print(f"   API 키: {OPENAI_API_KEY[:20]}...")
        print(f"   모델: {OPENAI_MODEL}")
    except Exception as e:
        print(f"❌ config 모듈 import 실패: {e}")
        return False
    
    try:
        from components import AgentState, ToolManager
        print("✅ components 모듈 import 성공")
    except Exception as e:
        print(f"❌ components 모듈 import 실패: {e}")
        return False
    
    try:
        from workflow_nodes import agent, grade_documents, rewrite, generate
        print("✅ workflow_nodes 모듈 import 성공")
    except Exception as e:
        print(f"❌ workflow_nodes 모듈 import 실패: {e}")
        return False
    
    try:
        from workflow_graph import AgenticRAGWorkflow
        print("✅ workflow_graph 모듈 import 성공")
    except Exception as e:
        print(f"❌ workflow_graph 모듈 import 실패: {e}")
        return False
    
    print("✅ 모든 모듈 import 성공!")
    return True

def test_basic_functionality():
    """기본 기능을 테스트합니다."""
    print("\n=== 기본 기능 테스트 ===")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # 간단한 LLM 테스트
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        response = llm.invoke("안녕하세요!")
        print(f"✅ LLM 테스트 성공: {response.content}")
        
    except Exception as e:
        print(f"❌ LLM 테스트 실패: {e}")
        return False
    
    return True

def test_workflow_creation():
    """워크플로우 생성을 테스트합니다."""
    print("\n=== 워크플로우 생성 테스트 ===")
    
    try:
        from workflow_graph import AgenticRAGWorkflow
        
        # 워크플로우 생성 (데이터 파이프라인 없이)
        workflow = AgenticRAGWorkflow()
        workflow.build_workflow()
        
        print("✅ 워크플로우 생성 성공")
        return True
        
    except Exception as e:
        print(f"❌ 워크플로우 생성 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Agentic RAG 시스템 테스트 시작")
    print("=" * 50)
    
    # 1. Import 테스트
    if not test_imports():
        print("❌ Import 테스트 실패")
        return
    
    # 2. 기본 기능 테스트
    if not test_basic_functionality():
        print("❌ 기본 기능 테스트 실패")
        return
    
    # 3. 워크플로우 생성 테스트
    if not test_workflow_creation():
        print("❌ 워크플로우 생성 테스트 실패")
        return
    
    print("\n🎉 모든 테스트 통과! 시스템이 정상적으로 작동합니다.")
    print("이제 main.py를 실행하여 전체 시스템을 사용할 수 있습니다.")

if __name__ == "__main__":
    main()
