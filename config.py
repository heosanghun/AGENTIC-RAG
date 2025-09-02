import os
from dotenv import load_dotenv

# .env 파일 로드 (선택적)
try:
    load_dotenv()
except:
    pass

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# 문서 처리 설정
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# 벡터 스토어 설정
COLLECTION_NAME = "rag-chroma"

# 웹 크롤링 URL 목록
CRAWLING_URLS = [
    "https://finance.naver.com/",
    "https://finance.yahoo.com/",
    "https://finance.daum.net/",
]

# API 키가 환경 변수에 없는 경우 직접 설정
if not OPENAI_API_KEY:
    OPENAI_API_KEY = "your_openai_api_key_here"

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
