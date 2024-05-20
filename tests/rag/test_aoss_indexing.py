

import os
import json
import sys

sys.path.append("../lib/shared/file-import-batch-job")


class TestAossIndexingFeatures:

    def __init__(self) -> None:
        pass

    def get_mock_data(self):
        # mock_data_name = "aoss_pdf_indexing_01.json"
        # mock_data_name = "aoss_pdf_indexing_02.json"
        # mock_data_name = "aoss_pdf_indexing_03.json"
        mock_data_name = "aoss_pdf_indexing_04.json"
        with open(os.path.join("mock-data", mock_data_name), "r") as f:
            test_data = json.load(f)    

        return test_data

    def test_pdf_indexing_feature(self):

        test_data = self.get_mock_data()

        for key in test_data:
            env_name = key.upper()
            os.environ[env_name] = test_data[key]
        
        from main import main as file_import_main
        file_import_main()

    def run(self):
        self.test_pdf_indexing_feature()


    # Testing for AOSS
    def check_indexed_data(self):
        from genai_core.opensearch.client import get_open_search_client

        client = get_open_search_client()

        test_data = self.get_mock_data()
        index_name = test_data["workspace_id"].replace("-", "")

        print(index_name)

        # doc_id = "1%3A0%3A_VDId48BuDs0q5s-sCJ_"
        doc_id = "1%3A0%3AI1A5hY8BuDs0q5s-UCOh"

        # query = {
        #     "query": {
        #         "ids": {
        #             "values": [doc_id]
        #         }
        #     }
        # }

        # query = {
        #     "query": {
        #         "term": {
        #             "_id": {
        #                 "value": doc_id
        #             }
        #         }
        #     }
        # }

        query = {
            "query": {
                "term": {
                    "_id": doc_id
                }
            }
        }

        response = client.search(
            index = index_name,
            body = query,
        )

        # response = client.get(index=index_name, id=doc_id)

        print(response)
