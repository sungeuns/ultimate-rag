
## 로컬 환경에서 디버깅하고 배포하기

아래와 같은 순서로 이뤄집니다.
1. CDK를 활용해서 사용자의 AWS 계정에 배포를 진행합니다.
1. 로컬 개발 환경을 구성합니다.
1. mock data를 활용하여 각 서비스의 동작을 로컬 환경에서 테스트합니다.


## 배포 진행

- 배포 방법은 [deploy guide](../guide/deploy.md) 를 참고해 주세요.

### 배포 관련 Troubleshooting

#### Container 빌드 관련

로컬 환경에서 docker image를 빌드하기 때문에 만일 `docker`를 사용하는 경우 충분한 공간이 있는지 확인이 필요합니다.
- 부족하다면 `docker system prune -a` 를 사용해서 공간을 확보합니다.

MacOS 에서 `docker` 대신 `finch`를 사용하는 경우
- `no space left on device` 발생 시 
  - 문서 참고 : https://runfinch.com/docs/managing-finch/macos/disk-management/#disk-size
- CDK 배포 시 `CDK_DOCKER` 환경변수를 아래와 같이 설정해 주어야 합니다.
  - `CDK_DOCKER=finch npx cdk deploy`
  - 예시 스크립트 참고 : `scripts/cdk_deploy_finch.sh`

#### x86/arm64 아키텍쳐 관련

- `dockerx` 를 사용해서 cross-platform 빌드가 가능하지만, 동작하지 않는 경우가 있습니다.
  - 따라서 기본적으로는 빌드하는 플랫폼과 동일한 플랫폼을 사용하게 됩니다.
  - ARM 기반 서버 및 apple silicon인 경우 `ARM_64`, 일반적인 X86 서버인 경우 `X86_64`
- 만일 특정 플랫폼으로 빌드하고 싶다면 `lib/shared/index.ts` 파일에서 적절한 컨테이너 빌드를 위한 아키텍쳐를 지정해 줄 필요가 있습니다.
  - `ARM_64` : `const lambdaArchitecture = lambda.Architecture.ARM_64;`
  - `X86_64` : `const lambdaArchitecture = lambda.Architecture.X86_64;`


## 로컬 개발 환경 구성

#### Python 패키지

- 각 모듈 별 `requirements.txt`에 있는 파일들만 설치해도 되지만, 아래 패키지들이 추가로 필요할 수 있습니다.

  ```
  # 로컬 환경에서 개발 시
  pip install python-dotenv

  # PDF 파싱 시 (배포 시에는 docker image를 사용하기 때문에 로컬 환경에서는 추가 설치 필요)
  pip install unstructured
  pip install "unstructured[pdf]"

  # MacOS에서 poppler 추가 설치
  conda install poppler

  # langchain 의 경우 기존 requirements.txt에 있는 것으로 설치해도 상관없습니다.
  pip install langchain==0.1.20
  pip install langchain-community==0.0.38
  pip install langsmith==0.1.57
  ```

- 배포 시에는 로컬 환경에서 성공한 패키지 버전으로 업데이트하는 것이 좋습니다.
- 예를 들어, `lib/shared/file-import-dockerfile` 의 경우 아래와 같이 로컬 환경에서 새로운 버전의 패키지를 활용했다면 컨테이너 버전 등을 수정해야 배포 시 정상 동작하게 됩니다.

  ```
  # FROM quay.io/unstructured-io/unstructured:0.11.2
  FROM quay.io/unstructured-io/unstructured:0.13.7  # Use the successful version which tested
  ```

- 아래의 `requirements.txt` 도 성공한 버전에 맞추어 수정해 주어야 배포 시 정상 동작하게 됩니다.
  - `lib/shared/layers/common/requirements.txt`
  - `lib/shared/file-import-batch-job/requirements.txt`


#### 환경 변수 설정

- CDK 활용핸 배포가 성공한 이후에 수행합니다.
- 로컬 테스를 진행하기 위해서는 로컬 AWS credential 에 해당 권한이 있어야 합니다.
- `tests/.env` 파일을 생성하고 배포한 AOSS, Kendra, DynamoDB, SQS, SNS, ... 등등 사용하는 여러 서비스와 관련된 값을 입력합니다.
- 아래는 `.env`의 예시입니다. 모든 값이 반드시 필요한 것은 아니고 로컬 환경에서 개발/테스트 할 때 필요한 환경변수만 넣어주어도 상관없습니다.
  - 해당 값들은 cdk로 배포된 lambda 등의 configuration에서 확인이 가능합니다.

```
AWS_REGION=us-west-2

LOG_LEVEL=INFO
OPEN_SEARCH_COLLECTION_ENDPOINT=https://mrddjnm6dhio5okny662.us-west-2.aoss.amazonaws.com
OPEN_SEARCH_COLLECTION_ENDPOINT_PORT=443
OPEN_SEARCH_COLLECTION_NAME=llm-chat-dev-genaichatbot-wo
POWERTOOLS_DEV=true
POWERTOOLS_LOGGER_LOG_EVENT=true
POWERTOOLS_SERVICE_NAME=chatbot
WORKSPACES_BY_OBJECT_TYPE_INDEX_NAME=by_object_type_idx
WORKSPACES_TABLE_NAME=llm-chat-devGenAIChatBotStack-RagEnginesRagDynamoDBTablesWorkspacesD2D3C0C4-LQQQMVIYR81J

DOCUMENTS_BY_COMPOUND_KEY_INDEX_NAME=by_compound_key_idx
DOCUMENTS_BY_STATUS_INDEX=by_status_idx
DOCUMENTS_TABLE_NAME=llm-chat-devGenAIChatBotStack-RagEnginesRagDynamoDBTablesDocumentsF6F2B272-4ML769BWD33Y
PROCESSING_BUCKET_NAME=llm-chat-devgenaichatbots-ragenginesdataimportproc-bx13ddia9ztc

API_KEYS_SECRETS_ARN=arn:aws:secretsmanager:us-west-2:723597067299:secret:SharedApiKeysSecret9EA666ED-tuhRyQdJdRfK-2D6gfi
CONFIG_PARAMETER_NAME=CFN-SharedConfig358B4A20-e6zFunNqRa2K
SNS_TOPIC_ARN=arn:aws:sns:us-west-2:723597067299:llm-chat-devGenAIChatBotStack-ChatBotApiRealtimeMessagesTopicCC5C5EA4-7DYgkB2f850D
MESSAGES_TOPIC_ARN=arn:aws:sns:us-west-2:723597067299:llm-chat-devGenAIChatBotStack-ChatBotApiRealtimeMessagesTopicCC5C5EA4-7DYgkB2f850D

AWS_NODEJS_CONNECTION_REUSE_ENABLED=1
GRAPHQL_ENDPOINT=https://4dyslp5onzeotprl6bye7dov6m.appsync-api.us-west-2.amazonaws.com/graphql

SAGEMAKER_RAG_MODELS_ENDPOINT=RagEnginesSageMakerModelMultiAB24AEndpoint6DA7D681-AYVexqh887yR
SESSIONS_BY_USER_ID_INDEX_NAME=byUserId
SESSIONS_TABLE_NAME=llm-chat-devGenAIChatBotStack-ChatBotApiChatDynamoDBTablesSessionsTable92B891E3-1MVBWG1LXY8GY

DEFAULT_KENDRA_INDEX_ID=56afa140-59b3-4402-88b5-8a5ada5aa1be
DEFAULT_KENDRA_INDEX_NAME=llm-chat-dev-genaichatbot-wo
DEFAULT_KENDRA_S3_DATA_SOURCE_BUCKET_NAME=llm-chat-devgenaichatbots-ragengineskendraretrieva-remrfwmaip3o
DEFAULT_KENDRA_S3_DATA_SOURCE_ID=ac6c10fa-24f6-4e83-a276-4acdd9371f0f
DELETE_WORKSPACE_WORKFLOW_ARN=arn:aws:states:us-west-2:723597067299:stateMachine:RagEnginesWorkspacesDeleteWorkspace6908C6DA-pgl1BBgcMJ9u

UPLOAD_BUCKET_NAME=llm-chat-devgenaichatbots-ragenginesdataimportuplo-imywistfc3rb
USER_FEEDBACK_BUCKET_NAME=llm-chat-devgenaichatbots-chatbotapichatbucketsuse-zqpwj1ubar98
WEBSITE_CRAWLING_WORKFLOW_ARN=arn:aws:states:us-west-2:723597067299:stateMachine:RagEnginesDataImportWebsiteCrawlingWorkflowWebsiteCrawling9B1CEC96-5HOPtHm2ydoc
X_ORIGIN_VERIFY_SECRET_ARN=arn:aws:secretsmanager:us-west-2:723597067299:secret:SharedXOriginVerifySecret25-7TEnSxWZdkhh-AcP2Q2
CREATE_OPEN_SEARCH_WORKSPACE_WORKFLOW_ARN=arn:aws:states:us-west-2:723597067299:stateMachine:RagEnginesOpenSearchVectorCreateOpenSearchWorkspace2B2FCA5B-n8E0Ga8tlQZD

```

#### AOSS (Amazon OpenSearch Serverless) 기능까지 로컬에서 테스트하는 경우

- 기본적인 CDK 배포는 AOSS가 private VPC를 사용하도록 되어 있으므로, 로컬 환경에서 테스트 하려면 public 으로 설정해 줄 필요가 있습니다.
  - 문서 참고: https://docs.aws.amazon.com/ko_kr/opensearch-service/latest/developerguide/serverless-security.html#serverless-security-network
- Data access policy 또한 사용하는 IAM role 이 접근 가능하도록 설정 해 주어야 로컬에서 테스트가 가능합니다.
  - 기본적인 RAG 기능을 개발할 때는 아래 권한이 주로 활용됩니다.
    ```
    "aoss:DescribeIndex",
    "aoss:UpdateIndex",
    "aoss:ReadDocument",
    "aoss:WriteDocument",
    ```
  - 관련 문서 참고: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-data-access.html
- 또한 환경변수에 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` 값이 접근 가능한 정상적인 값으로 있어야 하며, 원하는 값이 있다면 `.env` 에 해당 값을 넣어주어도 됩니다.


#### Mock 데이터를 활용하여 로컬 개발환경 구성

이 경로 (`tests/mock-data`) 에 있는 샘플 데이터를 참고합니다.
- aoss_pdf_indexing_XXX : 파일을 업로드 하고 이를 AOSS에 인덱싱 하는 샘플입니다.
  - `workspace_id`, `document_id`, `input_bucket_name`, `input_object_key`, `processing_bucket_name`, `processing_object_key` 값을 모두 알맞게 변경해 주어야 합니다.
  - 해당 값들은 배포된 서비스에서 workspace에 파일을 직접 업로드 해 본 후, `step function`의 FileImport 를 위한 job 콘솔에서 `FileImportJob` 의 input parameter를 복사해서 사용하면 됩니다.
- semantic_search_XXX : 입력 쿼리를 넣었을 때 가장 유사한 문서를 검색하는 샘플입니다.
  - 검색 테스트 용도이며, `workspaceId` 와 `query` 만 수정해 주면 됩니다.
- llm_rag_request_XXX : RAG 테스트 샘플입니다.
  - `text` 와 `workspaceId` 만 알맞게 바꾸어 주면 됩니다.
  - 만일 Retrieval 없이 LLM 의 기능만 활용하려면 `workspaceId` 를 빼도 됩니다. (`llm_simple_request.json` 파일 참고)
  - 그 외 연속 대화를 하려면 `sessionId`, LLM 변경을 하려면 model id와 관련 파라미터를 바꾸어 주면 됩니다.


#### Frontend (React) 앱 로컬 테스트하기

Deploy 가이드의 [UI 로컬 테스트](../guide/deploy.md#run-user-interface-locally) 부분을 참고해 주세요.

- 로컬 테스트를 하는 경우에는 `lib/user-interface/react-app/src/common/constants.ts` 파일의 `getDistributionUrl()` 함수 부분에, 적절한 CloudFront distribution URL 값으로 바꾸어 주어야 RAG 검색 시 metadata에 포함된 이미지 등을 정상적으로 볼 수 있습니다.
  - 기본적으로 배포된 CF distribution url 을 동일하게 사용하므로, localhost 에서는 변경이 필요합니다.


#### Frontend - Backend API 변경하기

- 해당 코드는 GraphQL을 사용하며, 그렇기 때문에 `schema.graphql` 을 먼저 수정해 주어야 합니다.
- 그 후 아래 명령어를 사용해서 `API.ts` 와 같은 파일들이 자동으로 생성되도록 합니다.
  ```
  # From the project root
  $ npm run gen   # Check the package.json

  # Or you can use codegen directly
  $ amplify codegen
  ```


## 코드 수정 관련

#### 하드코딩된 parameter 들

- `lib/shared/file-import-batch-job/main.py` 
  ```
  # If true, complex workspace with PDF will add document summarization to the DB (DynamoDB)
  DOC_TYPE_COMPLEX_PDF_SUMMARIZATION = True
  ```

- `lib/shared/layers/python-sdk/python/genai_core/langchain/workspace_retriever.py`
  ```
  # If true, add document title and summary which summarized using LLM for search result.
  ADD_DOC_SUMMARY = True
  DOC_TOP_K = 3
  ```

- `lib/shared/layers/python-sdk/python/genai_core/opensearch/query.py`
  ```
  # Hybrid search score weight
  VECTOR_WEIGHT = 0.55
  KEYWORD_WEIGHT = 0.45
  ```



