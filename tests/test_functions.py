
import sys

sys.path.append("../lib/shared/layers/python-sdk/python")

from dotenv import load_dotenv
load_dotenv()


def test_sm_models():
    from sagemaker.test_cross_encoder import TestCrossEncoder
    test_cross_encoder = TestCrossEncoder()
    test_cross_encoder.run()


# 일반적인 Rest API 테스트
def test_rest_api_features():
    from rag.test_rest_api import TestRestApiFeatures
    test_api_features = TestRestApiFeatures()
    test_api_features.run()


# 검색 기능 테스트
def test_search_features():
    from rag.test_search import TestSearchFeatures
    test_search_features = TestSearchFeatures()
    test_search_features.run()


# LLM 활용한 결과 및 RAG 기반 결과 테스트
def test_llm_rag_features():
    from llm.test_llm_request import TestLLMFeatures
    test_llm_features = TestLLMFeatures()
    test_llm_features.run()


# AOSS에 데이터 인덱싱 테스트
def test_aoss_indexing_features():
    from rag.test_aoss_indexing import TestAossIndexingFeatures
    test_aoss_indexing = TestAossIndexingFeatures()
    test_aoss_indexing.run()
    # test_aoss_indexing.check_indexed_data()
    # test_aoss_indexing.delete_aoss_index()


# AOSS에 workspace (index) 생성 등의 기능 테스트
def test_aoss_manager():
    from rag.test_aoss_manager import TestAossManager
    test_aoss_manager = TestAossManager()
    test_aoss_manager.run()


def main():
    test_sm_models()
    # test_search_features()
    # test_llm_rag_features()
    # test_aoss_indexing_features()
    # test_rest_api_features()
    # test_aoss_manager()


if __name__ == "__main__":
    main()
