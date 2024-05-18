
import os
import json
import sys

sys.path.append("../lib/model-interfaces/langchain/functions/request-handler")
from index import handle_run as llm_handler

from common.test_utils import LambdaTestContext


class TestLLMFeatures:
    
    def __init__(self) -> None:
        self.test_context = LambdaTestContext("TestLLMFeatures")

    def get_test_data(self, data_name):
        with open(os.path.join("mock-data", data_name), "r") as f:
            test_data = json.load(f)

        return test_data

    def run(self):
        self.test_rag()
        # self.test_simple_llm()

    def test_rag(self):
        filename = "llm_rag_request_01.json"
        # filename = "llm_rag_request_02.json"
        # filename = "llm_rag_request_03.json"
        # filename = "llm_rag_request_04.json"
        test_event = self.get_test_data(filename)["message"]
        output = llm_handler(test_event)
        print("--------------------------------------------------")
        # meta = output["metadata"]
        gen_result = output["content"]
        print(gen_result)

    def test_simple_llm(self):
        filename = "llm_simple_request.json"
        test_event = self.get_test_data(filename)["message"]
        output = llm_handler(test_event)

        print(output)

