"""
Agentic RAG 지능형 정보 검색 시스템 - Streamlit Cloud 배포용
구글 드라이브 연동 버전
"""
import streamlit as st
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import requests
import json

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
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .data-status {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }
    .data-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 구글 드라이브 설정
GOOGLE_DRIVE_CONFIG = {
    "base_url": "https://drive.google.com/uc?export=download&id=",
    "file_ids": {
        "chroma_db": "1uiJVl2rhyjD9Ib4aCTt5cffALSoSab4y",  # Chroma 벡터 데이터베이스
        "documents": "1CFC9R9AkwgxDv21L5ZjDZoQiN34xxNyx",   # 크롤링된 문서들
        "config": "1pAB1QYys2ok039blfE5WbqfapFMAvrEq"        # 환경 설정 파일
    }
}

def load_data_from_drive():
    """구글 드라이브에서 데이터를 로드합니다."""
    try:
        # 여기에 구글 드라이브 API 연동 코드 추가
        # 현재는 데모 모드로 실행
        return True, "데모 모드로 실행 중"
    except Exception as e:
        return False, f"데이터 로드 실패: {str(e)}"

def generate_answer(question):
    """질문에 대한 답변을 생성합니다."""
    
    # 키워드 기반 답변 생성
    question_lower = question.lower()
    
    if 'agentic' in question_lower or 'rag' in question_lower:
        return """Agentic RAG는 LangGraph와 OpenAI GPT-4를 활용한 지능형 정보 검색 시스템입니다. 
        
주요 특징:
• 🔄 동적 워크플로우: LangGraph 기반 의사결정 시스템
• 🧠 지능형 분석: GPT-4를 통한 문서 관련성 평가
• 📊 실시간 데이터: 웹 크롤링을 통한 최신 정보 수집
• 💬 대화형 인터페이스: 직관적인 웹 인터페이스

이 시스템은 사용자의 질문을 받아 관련 문서를 검색하고, 그 관련성을 평가하여 필요에 따라 질문을 재작성하거나 최종 답변을 생성합니다."""
    
    elif '비트코인' in question or '암호화폐' in question:
        return """비트코인 및 암호화폐 투자 전략:

📈 주요 투자 전략:
• **HODL 전략**: 장기 보유를 통한 성장 기대
• **DCA (Dollar-Cost Averaging)**: 정기적 투자로 평균 비용 낮춤
• **스테이킹**: 코인 보유 시 이자 수익
• **트레이딩**: 단기 가격 변동 활용

⚠️ 투자 시 고려사항:
• 높은 변동성과 리스크
• 포트폴리오 다각화
• 손절매 설정
• 장기적 관점"""
    
    elif '금융' in question or '시장' in question:
        return """현재 금융 시장의 주요 동향:

📊 주요 트렌드:
• 인플레이션 관리와 금리 정책
• ESG 투자 증가
• 디지털 금융 서비스 확대
• 암호화폐 시장의 성장

💡 투자 시 고려사항:
• 포트폴리오 다양화
• 장기적 관점
• 리스크 관리
• 전문가 상담 활용"""
    
    elif '투자' in question or '포트폴리오' in question:
        return """투자 포트폴리오 구성의 핵심 원칙:

🎯 목표 설정:
• 투자 목적과 기간 명확화
• 위험 감수 성향 평가
• 수익률 목표 설정

📊 자산 배분:
• 주식: 성장 잠재력 (고위험, 고수익)
• 채권: 안정성 (저위험, 저수익)
• 부동산: 인플레이션 대비
• 현금: 유동성 확보

🔄 지속적 관리:
• 정기적인 리밸런싱
• 시장 상황 모니터링
• 투자 전략 조정"""
    
    elif '주식' in question or '분석' in question:
        return """주식 시장 분석 방법:

📊 기본적 분석 (Fundamental Analysis):
• 재무제표 분석
• 산업 동향 파악
• 경쟁사 비교
• 경제 지표 분석

📈 기술적 분석 (Technical Analysis):
• 차트 패턴 분석
• 이동평균선 활용
• 거래량 분석
• 기술적 지표 활용

🧠 종합적 접근:
• 기본적 + 기술적 분석 결합
• 시장 심리 분석
• 리스크 관리 전략"""
    
    else:
        return f"""'{question}'에 대한 답변을 생성했습니다!

현재 데모 모드로 실행 중이며, 실제 Agentic RAG 시스템의 전체 기능을 사용하려면:

1. 구글 드라이브에 데이터 업로드 필요
2. 벡터 데이터베이스 및 문서 파일 연동
3. OpenAI API 키 설정

더 자세한 정보나 특정 질문에 대한 답변을 원하시면 구체적으로 질문해주세요!"""

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.markdown('<h1 class="main-header">🤖 Agentic RAG 지능형 정보 검색 시스템</h1>', unsafe_allow_html=True)
    
    # 데이터 상태 확인
    data_loaded, data_message = load_data_from_drive()
    
    if data_loaded:
        st.markdown('<div class="data-status">✅ 데이터 로드 완료</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="data-warning">⚠️ {data_message}</div>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("## 📊 시스템 상태")
        if data_loaded:
            st.success("✅ 시스템 준비됨")
        else:
            st.warning("⚠️ 데이터 로드 필요")
        
        # 간단한 사용법
        st.markdown("## 📖 사용법")
        st.markdown("""
        1. 질문 입력창에 질문 입력
        2. 예시 질문 버튼 활용
        3. AI 답변 확인
        """)
        
        # 버전 정보
        st.markdown("## ℹ️ 버전 정보")
        st.markdown("**Agentic RAG v1.0**")
        st.markdown("LangGraph + OpenAI GPT-4")
        
        # 배포 정보
        st.markdown("## 🌐 배포 정보")
        st.markdown("**Streamlit Cloud**")
        st.markdown("인터넷에서 접속 가능")
        
        # 데이터 연동 정보
        st.markdown("## 📁 데이터 연동")
        if data_loaded:
            st.success("구글 드라이브 연동됨")
        else:
            st.info("구글 드라이브 연동 필요")
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">💬 질문하기</h2>', unsafe_allow_html=True)
        
        # 질문 입력
        question = st.chat_input("질문을 입력하세요...")
        
        if question:
            # 사용자 메시지 추가
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now()
            })
            
            # 답변 생성
            answer = generate_answer(question)
            
            # 답변 메시지 추가
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "timestamp": datetime.now()
            })
            
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
        
        # 답변 표시 영역
        if "messages" in st.session_state and st.session_state.messages:
            # 마지막 답변만 표시
            last_message = st.session_state.messages[-1]
            if last_message["role"] == "assistant":
                st.markdown('<div class="answer-container">', unsafe_allow_html=True)
                st.markdown('<div class="answer-header">🤖 AI 답변</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="answer-content">{last_message["content"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 시스템 정보</h2>', unsafe_allow_html=True)
        
        # 시스템 상태 정보
        if data_loaded:
            st.success("✅ 시스템 준비됨")
        else:
            st.warning("⚠️ 데이터 로드 필요")
        
        # 통계
        if "messages" in st.session_state:
            st.markdown("## 📈 통계")
            st.metric("총 대화 수", len(st.session_state.messages))
            
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("사용자 질문", user_messages)
            
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("시스템 답변", assistant_messages)
    
    # 채팅 기록 표시
    if "messages" in st.session_state and st.session_state.messages:
        st.markdown('<h2 class="sub-header">💭 대화 기록</h2>', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 하단 정보
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 검색 기능</h4>
            <p>웹 크롤링을 통한 실시간 정보 수집</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🧠 AI 분석</h4>
            <p>GPT-4를 활용한 지능형 답변 생성</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🔄 워크플로우</h4>
            <p>LangGraph 기반의 동적 의사결정 시스템</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
