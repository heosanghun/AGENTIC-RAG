"""
데이터 파이프라인: 웹 크롤링 및 벡터 스토어 구축
"""
import logging
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CRAWLING_URLS, CHUNK_SIZE, CHUNK_OVERLAP, COLLECTION_NAME

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    """웹 크롤링 및 벡터 스토어 구축을 위한 데이터 파이프라인"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.vectorstore = None
        self.retriever = None
    
    def crawl_documents(self, urls: List[str] = None) -> List:
        """웹 페이지에서 문서를 크롤링합니다."""
        if urls is None:
            urls = CRAWLING_URLS
        
        logger.info(f"웹 크롤링 시작: {len(urls)}개 URL")
        
        try:
            docs = []
            for url in urls:
                try:
                    logger.info(f"크롤링 중: {url}")
                    loader = WebBaseLoader(url)
                    doc = loader.load()
                    docs.extend(doc)
                    logger.info(f"성공: {url}에서 {len(doc)}개 문서 로드")
                except Exception as e:
                    logger.error(f"크롤링 실패 {url}: {str(e)}")
                    continue
            
            logger.info(f"총 {len(docs)}개 문서 크롤링 완료")
            return docs
            
        except Exception as e:
            logger.error(f"크롤링 중 오류 발생: {str(e)}")
            raise
    
    def split_documents(self, documents: List) -> List:
        """문서를 청크로 분할합니다."""
        logger.info("문서 분할 시작")
        
        try:
            doc_splits = self.text_splitter.split_documents(documents)
            logger.info(f"문서 분할 완료: {len(doc_splits)}개 청크")
            return doc_splits
        except Exception as e:
            logger.error(f"문서 분할 중 오류 발생: {str(e)}")
            raise
    
    def create_vectorstore(self, documents: List):
        """벡터 스토어를 생성하고 문서를 저장합니다."""
        logger.info("벡터 스토어 생성 시작")
        
        try:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                collection_name=COLLECTION_NAME,
                embedding=self.embeddings,
            )
            
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # 상위 5개 문서 검색
            )
            
            logger.info("벡터 스토어 생성 완료")
            
        except Exception as e:
            logger.error(f"벡터 스토어 생성 중 오류 발생: {str(e)}")
            raise
    
    def build_pipeline(self) -> 'DataPipeline':
        """전체 파이프라인을 구축합니다."""
        logger.info("데이터 파이프라인 구축 시작")
        
        try:
            # 1. 문서 크롤링
            documents = self.crawl_documents()
            
            # 2. 문서 분할
            doc_splits = self.split_documents(documents)
            
            # 3. 벡터 스토어 생성
            self.create_vectorstore(doc_splits)
            
            logger.info("데이터 파이프라인 구축 완료")
            return self
            
        except Exception as e:
            logger.error(f"파이프라인 구축 실패: {str(e)}")
            raise
    
    def get_retriever(self):
        """검색기를 반환합니다."""
        if self.retriever is None:
            raise ValueError("검색기가 초기화되지 않았습니다. build_pipeline()을 먼저 실행하세요.")
        return self.retriever
    
    def get_vectorstore(self):
        """벡터 스토어를 반환합니다."""
        if self.vectorstore is None:
            raise ValueError("벡터 스토어가 초기화되지 않았습니다. build_pipeline()을 먼저 실행하세요.")
        return self.vectorstore

def main():
    """메인 실행 함수"""
    try:
        pipeline = DataPipeline()
        pipeline.build_pipeline()
        print("데이터 파이프라인 구축이 완료되었습니다!")
        
        # 검색기 테스트
        retriever = pipeline.get_retriever()
        test_query = "금융"
        results = retriever.get_relevant_documents(test_query)
        print(f"테스트 쿼리 '{test_query}'에 대한 {len(results)}개 결과")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
