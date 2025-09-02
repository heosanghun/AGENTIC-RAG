# 🤖 Agentic RAG 지능형 정보 검색 시스템

LangGraph와 OpenAI GPT-4를 활용하여 구축된 지능형 정보 검색 시스템입니다. 사용자의 질문을 받으면 관련 문서를 검색하고, 그 관련성을 평가하여 필요에 따라 질문을 재작성하거나 최종 답변을 생성합니다.

## 🌟 주요 특징

- **🔄 동적 워크플로우**: LangGraph를 활용한 유연한 의사결정 시스템
- **🧠 지능형 분석**: GPT-4를 통한 문서 관련성 평가 및 답변 생성
- **📊 실시간 데이터**: 웹 크롤링을 통한 최신 정보 수집
- **💬 대화형 인터페이스**: Streamlit을 통한 직관적인 웹 인터페이스
- **📈 성능 모니터링**: 각 단계별 실행 결과 및 통계 제공

## 🏗️ 시스템 아키텍처

```
사용자 질문 → Agent → Retrieve → Grade Documents → Generate/Rewrite → 최종 답변
```

### 핵심 컴포넌트

1. **Agent**: 사용자 질문 분석 및 도구 호출 결정
2. **Retrieve**: 벡터 데이터베이스에서 관련 문서 검색
3. **Grade Documents**: 검색된 문서의 관련성 평가
4. **Generate**: 관련성 높은 문서 기반 답변 생성
5. **Rewrite**: 관련성 낮을 때 질문 재작성

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd agentic-rag

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`env_example.txt` 파일을 `.env`로 복사하고 OpenAI API 키를 설정하세요:

```bash
cp env_example.txt .env
# .env 파일에 API 키 입력
OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. 실행 방법

#### 방법 1: Streamlit 웹 인터페이스 (권장)

```bash
streamlit run streamlit_app.py
```

웹 브라우저에서 `http://localhost:8501`로 접속하여 사용하세요.

#### 방법 2: 명령줄 인터페이스

```bash
python main.py
```

#### 방법 3: 시스템 테스트

```bash
python test_system.py
```

## 📁 프로젝트 구조

```
agentic-rag/
├── config.py              # 설정 관리
├── components.py           # 핵심 컴포넌트 (상태 관리, 도구)
├── data_pipeline.py       # 데이터 파이프라인 (크롤링, 벡터 스토어)
├── workflow_nodes.py      # 워크플로우 노드 구현
├── workflow_graph.py      # LangGraph 워크플로우 구성
├── main.py                # 메인 실행 파일
├── streamlit_app.py       # Streamlit 웹 인터페이스
├── test_system.py         # 시스템 테스트
├── requirements.txt       # 의존성 목록
├── env_example.txt       # 환경 변수 예시
└── README.md             # 프로젝트 문서
```

## 💻 사용법

### Streamlit 웹 인터페이스

1. **시스템 초기화**: 사이드바의 "🔄 시스템 초기화" 버튼 클릭
2. **질문 입력**: 채팅 입력창에 질문 입력
3. **답변 확인**: AI가 생성한 답변 확인
4. **예시 질문**: 오른쪽 패널의 예시 질문 버튼 활용

### 예시 질문

- "agentic rag가 어떤 의미야?"
- "금융 시장의 최신 동향은?"
- "투자 포트폴리오 구성 방법은?"
- "주식 시장 분석 방법은?"
- "암호화폐 투자 전략은?"

## 🔧 기술 스택

- **LangChain**: RAG 파이프라인 구축
- **LangGraph**: 워크플로우 및 상태 관리
- **OpenAI GPT-4**: 지능형 의사결정 및 답변 생성
- **Chroma**: 벡터 데이터베이스
- **BeautifulSoup**: 웹 크롤링
- **Streamlit**: 웹 인터페이스
- **Python**: 백엔드 로직

## 📊 성능 지표

- **처리 속도**: 질문당 평균 2-5초
- **정확도**: 문서 관련성 평가를 통한 품질 향상
- **확장성**: 모듈화된 구조로 쉬운 기능 확장
- **안정성**: 예외 처리 및 오류 복구 메커니즘

## 🛠️ 개발 및 확장

### 새로운 노드 추가

1. `workflow_nodes.py`에 노드 함수 구현
2. `workflow_graph.py`에 노드 추가 및 엣지 설정
3. 필요한 도구 및 상태 관리 로직 구현

### 새로운 데이터 소스 추가

1. `data_pipeline.py`에 크롤링 로직 추가
2. `config.py`에 URL 목록 업데이트
3. 벡터 스토어 설정 조정

## 🐛 문제 해결

### 일반적인 오류

1. **API 키 오류**: `.env` 파일 확인 및 API 키 재설정
2. **의존성 충돌**: `pip install -r requirements.txt` 재실행
3. **메모리 부족**: `CHUNK_SIZE` 및 `CHUNK_OVERLAP` 조정

### 로그 확인

```bash
# Streamlit 로그
streamlit run streamlit_app.py --logger.level debug

# 시스템 로그
tail -f agentic_rag.log
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

**🎉 Agentic RAG 시스템을 즐겁게 사용하세요!**
