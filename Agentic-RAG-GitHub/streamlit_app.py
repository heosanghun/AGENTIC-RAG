"""
Agentic RAG 지능형 정보 검색 시스템 - Streamlit 웹 인터페이스
"""
import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

# 페이지 설정
st.set_page_config(
    page_title="Agentic RAG 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .system-message {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .status-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .answer-container {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .answer-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #495057;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #dee2e6;
    }
    .answer-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #212529;
    }
    .metadata-box {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    """시스템을 초기화하고 워크플로우를 생성합니다."""
    try:
        from workflow_graph import AgenticRAGWorkflow
        from data_pipeline import DataPipeline
        
        with st.spinner("🔄 시스템 초기화 중..."):
            # 데이터 파이프라인 구축
            pipeline = DataPipeline()
            pipeline.build_pipeline()
            
            # 워크플로우 생성
            workflow = AgenticRAGWorkflow(pipeline)
            workflow.build_workflow()
            
        st.success("✅ 시스템 초기화 완료!")
        return workflow
    except Exception as e:
        st.error(f"❌ 시스템 초기화 실패: {str(e)}")
        return None

def display_chat_history():
    """채팅 기록을 표시합니다."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 메타데이터가 있는 경우 표시
            if "metadata" in message and message["metadata"]:
                with st.expander("📊 메타데이터"):
                    st.json(message["metadata"])

def add_message(role, content, metadata=None):
    """메시지를 채팅 기록에 추가합니다."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(),
        "metadata": metadata
    })

def process_question(workflow, question):
    """질문을 처리하고 답변을 생성합니다."""
    try:
        with st.spinner(" 질문을 분석하고 답변을 생성하는 중..."):
            # 워크플로우 실행
            results = workflow.run_workflow(question)
            
            # 결과 처리
            if results:
                # 마지막 결과에서 답변 추출
                last_result = results[-1]
                if isinstance(last_result, tuple) and len(last_result) == 2:
                    node_name, result_data = last_result
                    
                    # 메시지에서 답변 추출
                    if "messages" in result_data and result_data["messages"]:
                        answer = result_data["messages"][-1].content
                        
                        # 메타데이터 구성
                        metadata = {
                            "node_name": node_name,
                            "total_nodes": len(results),
                            "processing_time": time.time(),
                            "workflow_path": [r[0] for r in results]
                        }
                        
                        return answer, metadata
            
            return "죄송합니다. 답변을 생성할 수 없습니다.", {"error": "No response generated"}
            
    except Exception as e:
        st.error(f"질문 처리 중 오류 발생: {str(e)}")
        return f"오류가 발생했습니다: {str(e)}", {"error": str(e)}

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.markdown('<h1 class="main-header">🤖 Agentic RAG 지능형 정보 검색 시스템</h1>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("## 📊 시스템 상태")
        
        # 시스템 초기화 버튼
        if st.button("🔄 시스템 초기화", type="primary"):
            st.session_state.workflow = initialize_system()
        
        # 시스템 정보
        if "workflow" in st.session_state and st.session_state.workflow:
            st.success("✅ 시스템 준비됨")
        else:
            st.warning("⚠️ 시스템이 초기화되지 않았습니다.")
        
        # 간단한 사용법
        st.markdown("## 📖 사용법")
        st.markdown("""
        1. **시스템 초기화** 버튼 클릭
        2. 질문 입력창에 질문 입력
        3. 예시 질문 버튼 활용
        4. AI 답변 확인
        """)
        
        # 버전 정보
        st.markdown("## ℹ️ 버전 정보")
        st.markdown("**Agentic RAG v1.0**")
        st.markdown("LangGraph + OpenAI GPT-4")
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">💬 질문하기</h2>', unsafe_allow_html=True)
        
        # 질문 입력
        question = st.chat_input("질문을 입력하세요...")
        
        if question:
            # 사용자 메시지 추가
            add_message("user", question)
            
            # 시스템이 초기화되지 않은 경우
            if "workflow" not in st.session_state or not st.session_state.workflow:
                st.error("⚠️ 시스템을 먼저 초기화해주세요. 사이드바의 '시스템 초기화' 버튼을 클릭하세요.")
                return
            
            # 질문 처리
            answer, metadata = process_question(st.session_state.workflow, question)
            
            # 답변 메시지 추가
            add_message("assistant", answer, metadata)
            
            # 페이지 새로고침
            st.rerun()
        
        # 예시 질문 (질문 입력창 바로 아래)
        st.markdown('<h3 class="sub-header">📋 예시 질문</h3>', unsafe_allow_html=True)
        
        example_questions = [
            "agentic rag가 어떤 의미야?",
            "금융 시장의 최신 동향은?",
            "투자 포트폴리오 구성 방법은?",
            "주식 시장 분석 방법은?",
            "암호화폐 투자 전략은?",
            "부동산 투자 시 고려사항은?",
            "은퇴 계획 수립 방법은?",
            "리스크 관리 전략은?"
        ]
        
        # 2열로 예시 질문 배치
        cols = st.columns(2)
        for i, example in enumerate(example_questions):
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(f"💡 {example[:25]}...", key=f"example_{i}", use_container_width=True):
                    st.session_state.example_question = example
                    st.rerun()
        
        # 답변 표시 영역 (빨간색 가이드선 영역)
        if "messages" in st.session_state and st.session_state.messages:
            # 마지막 답변만 표시
            last_message = st.session_state.messages[-1]
            if last_message["role"] == "assistant":
                st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                st.markdown('<div class="answer-header">🤖 AI 답변</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="answer-content">{last_message["content"]}</div>', unsafe_allow_html=True)
                
                # 메타데이터 표시
                if "metadata" in last_message and last_message["metadata"]:
                    with st.expander("📊 처리 정보"):
                        st.json(last_message["metadata"])
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 시스템 정보</h2>', unsafe_allow_html=True)
        
        # 시스템 상태 정보
        if "workflow" in st.session_state and st.session_state.workflow:
            st.success("✅ 시스템 준비됨")
            
            # 워크플로우 정보
            with st.expander("🔧 워크플로우 정보"):
                try:
                    mermaid_diagram = st.session_state.workflow.visualize_graph()
                    if mermaid_diagram:
                        st.code(mermaid_diagram, language="mermaid")
                except:
                    st.info("워크플로우 다이어그램을 표시할 수 없습니다.")
        else:
            st.warning("⚠️ 시스템이 초기화되지 않았습니다.")
        
        # 통계
        if "messages" in st.session_state:
            st.markdown("## 📈 통계")
            st.metric("총 대화 수", len(st.session_state.messages))
            
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("사용자 질문", user_messages)
            
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("시스템 답변", assistant_messages)

if __name__ == "__main__":
    main()
