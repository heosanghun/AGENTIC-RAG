# 📁 구글 드라이브 데이터 연동 가이드

## 🎯 **업로드가 필요한 데이터 파일들**

### **1. 벡터 데이터베이스 (Chroma DB)**
```
chroma_db/
├── chroma.sqlite3          # 메타데이터 저장소
├── embeddings/             # 임베딩 벡터 파일들
│   ├── embeddings-0.parquet
│   └── ...
└── index/                  # 인덱스 파일들
    ├── index-0.parquet
    └── ...
```

### **2. 크롤링된 문서 데이터**
```
crawled_documents/
├── finance_naver.txt       # 네이버 금융 문서
├── finance_yahoo.txt       # 야후 금융 문서
└── finance_daum.txt        # 다음 금융 문서
```

### **3. 환경 설정 파일**
```
.env                        # OpenAI API 키 등 환경 변수
```

## 🚀 **구글 드라이브 업로드 단계**

### **1단계: 폴더 구조 생성**
구글 드라이브에 다음 폴더 구조를 만드세요:

```
📁 Agentic-RAG-Data/
├── 📁 chroma_db/          # 벡터 데이터베이스
├── 📁 documents/           # 크롤링된 문서
└── 📄 .env                 # 환경 설정 파일
```

### **2단계: 파일 업로드**

#### **벡터 데이터베이스 업로드**
1. 로컬 `chroma_db/` 폴더 전체를 압축
2. 구글 드라이브 `chroma_db/` 폴더에 업로드
3. 폴더 ID 복사 (URL에서 확인)

#### **문서 데이터 업로드**
1. `crawled_documents/` 폴더의 모든 `.txt` 파일 업로드
2. 폴더 ID 복사

#### **환경 설정 파일 업로드**
1. `.env` 파일을 `Agentic-RAG-Data/` 폴더에 업로드
2. 파일 ID 복사

### **3단계: 폴더/파일 ID 확인**

#### **폴더 ID 확인 방법**
1. 구글 드라이브에서 폴더 우클릭
2. "링크 복사" 선택
3. URL에서 폴더 ID 추출:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```

#### **파일 ID 확인 방법**
1. 파일 우클릭 → "링크 복사"
2. URL에서 파일 ID 추출:
   ```
   https://drive.google.com/file/d/FILE_ID_HERE/view
   ```

## ⚙️ **Streamlit Cloud 설정**

### **1단계: 환경 변수 설정**
Streamlit Cloud → App Settings → Secrets에 추가:

```toml
[GOOGLE_DRIVE]
CHROMA_DB_FOLDER_ID = "your_chroma_db_folder_id"
DOCUMENTS_FOLDER_ID = "your_documents_folder_id"
CONFIG_FILE_ID = "your_env_file_id"

[OPENAI]
API_KEY = "your_openai_api_key"
```

### **2단계: 코드 수정**
`streamlit_cloud_app.py`의 `GOOGLE_DRIVE_CONFIG` 수정:

```python
GOOGLE_DRIVE_CONFIG = {
    "base_url": "https://drive.google.com/uc?export=download&id=",
    "file_ids": {
        "chroma_db": "실제_CHROMA_DB_폴더_ID",
        "documents": "실제_DOCUMENTS_폴더_ID",
        "config": "실제_ENV_파일_ID"
    }
}
```

## 🔧 **데이터 로딩 함수 구현**

### **구글 드라이브 API 연동**
```python
import gdown
import os

def download_from_drive(folder_id, local_path):
    """구글 드라이브 폴더를 로컬에 다운로드"""
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    gdown.download_folder(url, local_path, quiet=False)

def load_data_from_drive():
    """구글 드라이브에서 데이터 로드"""
    try:
        # 임시 디렉토리 생성
        temp_dir = "/tmp/agentic_rag_data"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 데이터 다운로드
        download_from_drive(
            GOOGLE_DRIVE_CONFIG["file_ids"]["chroma_db"],
            f"{temp_dir}/chroma_db"
        )
        
        download_from_drive(
            GOOGLE_DRIVE_CONFIG["file_ids"]["documents"],
            f"{temp_dir}/documents"
        )
        
        return True, "데이터 로드 완료"
    except Exception as e:
        return False, f"데이터 로드 실패: {str(e)}"
```

## 📋 **필요한 패키지 추가**

`requirements.txt`에 추가:
```
gdown>=4.7.1
requests>=2.31.0
```

## ⚠️ **주의사항**

1. **파일 크기**: 구글 드라이브 무료 계정은 15GB 제한
2. **공유 설정**: 폴더를 "링크가 있는 모든 사용자"로 공유
3. **API 제한**: 구글 드라이브 API 호출 제한 확인
4. **보안**: `.env` 파일에 API 키 포함 시 주의

## 🎉 **완료 후 확인사항**

1. ✅ 구글 드라이브에 모든 데이터 업로드
2. ✅ 폴더/파일 ID 확인 및 코드 수정
3. ✅ Streamlit Cloud 환경 변수 설정
4. ✅ 앱 재배포 및 테스트

이제 구글 드라이브를 통해 데이터를 연동하여 완전한 Agentic RAG 시스템을 Streamlit Cloud에서 실행할 수 있습니다!
