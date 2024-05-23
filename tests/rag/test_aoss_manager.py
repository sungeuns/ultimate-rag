

import os
import json
import sys

sys.path.append("../lib/rag-engines/opensearch-vector/functions/create-workflow/create")
from index import lambda_handler as create_aoss_workspace


from common.test_utils import LambdaTestContext


class TestAossManager:

    def __init__(self) -> None:
        self.test_context = LambdaTestContext("TestAossManager")

    def get_mock_data(self):
        mock_data_name = "create_aoss_index.json"
        with open(os.path.join("mock-data", mock_data_name), "r") as f:
            test_data = json.load(f)    

        return test_data
    
    def create_aoss_index(self):
        test_data = self.get_mock_data()

        create_aoss_workspace(
            event=test_data,
            context=self.test_context,
        )

    def run(self):
        self.create_aoss_index()
