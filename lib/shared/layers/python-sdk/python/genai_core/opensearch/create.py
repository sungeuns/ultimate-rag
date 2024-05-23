from .client import get_open_search_client


def create_workspace_index(workspace: dict):
    workspace_id = workspace["workspace_id"]
    index_name = workspace_id.replace("-", "")
    embeddings_model_dimensions = workspace["embeddings_model_dimensions"]

    client = get_open_search_client()

    ef_search = 512
    index_body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": ef_search,
            }
        },
        "mappings": {
            "properties": {
                "content_embeddings": {
                    "type": "knn_vector",
                    "dimension": int(embeddings_model_dimensions),
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {"ef_construction": 512, "m": 16},
                    },
                },
                "chunk_id": {"type": "keyword"},
                "workspace_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "document_sub_id": {"type": "keyword"},
                "document_type": {"type": "keyword"},
                "document_sub_type": {"type": "keyword"},
                "path": {"type": "text"},
                "language": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "content_complement": {"type": "text"},
                "metadata": {"type": "object"},
                "created_at": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis",
                },
            }
        },
    }

    """
    한국어의 경우 형태소 분석기 (nori) 추가사용
    - 그 외 언어
      - chinese: smartcn
      - japanese: kuromoji
    - AOSS supported plugin
      - https://docs.aws.amazon.com/ko_kr/opensearch-service/latest/developerguide/serverless-genref.html
    """

    languages = workspace["languages"]
    if "korean" in languages:
        index_body["mappings"]["properties"]["content"]["analyzer"] = "nori"
        index_body["mappings"]["properties"]["content_complement"]["analyzer"] = "nori"
    
    response = client.indices.create(index_name, body=index_body)

    print("Created workspace index")
    print(response)
