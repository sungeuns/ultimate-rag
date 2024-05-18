
import os
import json
import sys

sys.path.append("../lib/chatbot-api/functions/api-handler")
from index import handler as api_handler

from common.test_utils import LambdaTestContext


class TestRestApiFeatures:
    
    def __init__(self) -> None:
        self.test_context = LambdaTestContext("TestRestApiFeatures")

    def get_mock_data(self):
        filename = "create_workspace_complex.json"
        # filename = "create_workspace_normal.json"
        with open(os.path.join("mock-data", filename), "r") as f:
            test_data = json.load(f)

        return test_data

    def run(self):
        self.test_create_workspace()

    def test_create_workspace(self):
        test_data = self.get_mock_data()
        test_event = test_data["message"]
        result = api_handler(test_event, self.test_context)

        print(result)
