
import sys

sys.path.append("../lib/shared/layers/python-sdk/python")

from dotenv import load_dotenv
load_dotenv()


def test_rest_api_features():
    from rag.test_rest_api import TestRestApiFeatures
    test_api_features = TestRestApiFeatures()
    test_api_features.run()


def test_search_features():
    from rag.test_search import TestSearchFeatures
    test_search_features = TestSearchFeatures()
    test_search_features.run()


def test_llm_rag_features():
    from llm.test_llm_request import TestLLMFeatures
    test_llm_features = TestLLMFeatures()
    test_llm_features.run()


def test_aoss_indexing_features():
    from rag.test_aoss_indexing import TestAossIndexingFeatures
    test_aoss_indexing = TestAossIndexingFeatures()
    test_aoss_indexing.run()
    # test_aoss_indexing.check_indexed_data()


def main():
    # test_search_features()
    test_llm_rag_features()
    # test_aoss_indexing_features()
    # test_rest_api_features()


if __name__ == "__main__":
    main()
