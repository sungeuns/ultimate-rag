
import os
import json
import sys

sys.path.append("../lib/chatbot-api/functions/api-handler")
from index import handler as api_handler

from common.test_utils import LambdaTestContext


class TestSearchFeatures:
    
    def __init__(self) -> None:
        self.test_context = LambdaTestContext("TestSearchFeatures")

    def get_mock_data(self):
        # filename = "semantic_search_aoss_01.json"
        # filename = "semantic_search_aoss_02.json"
        filename = "semantic_search_aoss_03.json"
        # filename = "semantic_search_aoss_04.json"
        with open(os.path.join("mock-data", filename), "r") as f:
            test_data = json.load(f)

        return test_data

    def run(self):
        self.test_semantic_search()

    def test_semantic_search(self):
        test_data = self.get_mock_data()
        test_event = test_data["message"]
        result = api_handler(test_event, self.test_context)
        
        search_result = result.get("items", [])
        print(f"Num of search result: {len(search_result)}")

        for sr in search_result:
            file_path = sr["path"]
            # contents = sr["content"]
            metadata = sr["metadata"]
            v_score = sr["vectorSearchScore"]
            k_score = sr["keywordSearchScore"]
            score = sr["score"]
            print(f"Path: {file_path}, Vector score: {v_score}, Keyword score: {k_score}, Score: {score}")
            print(f"metadata: {metadata}")

            
            

