"""
간단한 Flask 웹 인터페이스 - Agentic RAG 시스템
"""
from flask import Flask, render_template_string, request, jsonify
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

app = Flask(__name__)

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Agentic RAG 시스템</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1f77b4 0%, #ff7f0e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .content {
            padding: 30px;
        }
        .chat-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .message {
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid;
        }
        .user-message {
            background: #e3f2fd;
            border-left-color: #2196f3;
            margin-left: 20%;
        }
        .assistant-message {
            background: #f3e5f5;
            border-left-color: #9c27b0;
            margin-right: 20%;
        }
        .input-container {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .input-container input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
        }
        .input-container button {
            padding: 15px 30px;
            background: #1f77b4;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .input-container button:hover {
            background: #1565c0;
        }
        .examples {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .example-btn {
            padding: 15px;
            background: #ff7f0e;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .example-btn:hover {
            background: #e65100;
        }
        .status {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        .error {
            background: #ffebee;
            border: 1px solid #f44336;
            color: #c62828;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agentic RAG 지능형 정보 검색 시스템</h1>
            <p>LangGraph와 OpenAI GPT-4를 활용한 지능형 정보 검색</p>
        </div>
        
        <div class="content">
            <div class="status" id="status">
                🚀 시스템이 준비되었습니다! 질문을 입력해보세요.
            </div>
            
            <div class="input-container">
                <input type="text" id="questionInput" placeholder="질문을 입력하세요..." onkeypress="handleKeyPress(event)">
                <button onclick="askQuestion()">질문하기</button>
            </div>
            
            <div class="examples">
                <button class="example-btn" onclick="askExample('agentic rag가 어떤 의미야?')">💡 Agentic RAG란?</button>
                <button class="example-btn" onclick="askExample('금융 시장의 최신 동향은?')">💡 금융 시장 동향</button>
                <button class="example-btn" onclick="askExample('투자 포트폴리오 구성 방법은?')">💡 포트폴리오 구성</button>
                <button class="example-btn" onclick="askExample('주식 시장 분석 방법은?')">💡 주식 시장 분석</button>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="message assistant-message">
                    안녕하세요! 🤖 Agentic RAG 시스템입니다. 
                    금융 관련 질문이나 다른 궁금한 점이 있으시면 언제든 물어보세요!
                </div>
            </div>
        </div>
    </div>

    <script>
        let chatHistory = [];
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                askQuestion();
            }
        }
        
        function askExample(question) {
            document.getElementById('questionInput').value = question;
            askQuestion();
        }
        
        function askQuestion() {
            const question = document.getElementById('questionInput').value.trim();
            if (!question) return;
            
            // 사용자 메시지 추가
            addMessage('user', question);
            document.getElementById('questionInput').value = '';
            
            // 상태 업데이트
            document.getElementById('status').innerHTML = '🤔 질문을 분석하고 답변을 생성하는 중...';
            document.getElementById('status').className = 'status loading';
            
            // API 호출
            fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage('assistant', data.answer);
                    document.getElementById('status').innerHTML = '✅ 답변이 생성되었습니다!';
                    document.getElementById('status').className = 'status';
                } else {
                    addMessage('assistant', '죄송합니다. 답변을 생성할 수 없습니다: ' + data.error);
                    document.getElementById('status').innerHTML = '❌ 오류가 발생했습니다: ' + data.error;
                    document.getElementById('status').className = 'status error';
                }
            })
            .catch(error => {
                addMessage('assistant', '죄송합니다. 시스템 오류가 발생했습니다.');
                document.getElementById('status').innerHTML = '❌ 시스템 오류: ' + error.message;
                document.getElementById('status').className = 'status error';
            });
        }
        
        function addMessage(role, content) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}-message`;
            messageDiv.textContent = content;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            chatHistory.push({ role, content, timestamp: new Date() });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'success': False, 'error': '질문이 입력되지 않았습니다.'})
        
        # 간단한 답변 생성 (실제로는 Agentic RAG 시스템 사용)
        answer = generate_simple_answer(question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def generate_simple_answer(question):
    """간단한 답변 생성 (실제 Agentic RAG 시스템 대신 사용)"""
    
    # 키워드 기반 간단한 답변
    question_lower = question.lower()
    
    if 'agentic' in question_lower or 'rag' in question_lower:
        return """Agentic RAG는 LangGraph와 OpenAI GPT-4를 활용한 지능형 정보 검색 시스템입니다. 
        
주요 특징:
• 🔄 동적 워크플로우: LangGraph 기반 의사결정 시스템
• 🧠 지능형 분석: GPT-4를 통한 문서 관련성 평가
• 📊 실시간 데이터: 웹 크롤링을 통한 최신 정보 수집
• 💬 대화형 인터페이스: 직관적인 웹 인터페이스

이 시스템은 사용자의 질문을 받아 관련 문서를 검색하고, 그 관련성을 평가하여 필요에 따라 질문을 재작성하거나 최종 답변을 생성합니다."""
    
    elif '금융' in question or '시장' in question:
        return """현재 금융 시장의 주요 동향은 다음과 같습니다:

📈 주요 트렌드:
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
        return f"""'{question}'에 대한 답변을 생성하는 중입니다...

현재 간단한 데모 모드로 실행 중이며, 실제 Agentic RAG 시스템의 전체 기능을 사용하려면:

1. 시스템 초기화가 필요합니다
2. 웹 크롤링 및 벡터 스토어 구축
3. LangGraph 워크플로우 실행

더 자세한 정보나 특정 질문에 대한 답변을 원하시면 구체적으로 질문해주세요!"""

if __name__ == '__main__':
    print("🚀 Flask 웹 서버 시작 중...")
    print("📍 웹 브라우저에서 http://localhost:5000 으로 접속하세요")
    print("🔄 서버를 중지하려면 Ctrl+C를 누르세요")
    app.run(debug=True, host='0.0.0.0', port=5000)
