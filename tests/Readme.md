


# How to dev/test in local env

### Install pacakges

```
# local dev
pip install python-dotenv

# pdf parsing
pip install unstructured
pip install "unstructured[pdf]"

# Install poppler in MacOS
conda install poppler

# Langchain updated needed
pip install langchain==0.1.20
pip install langchain-community==0.0.38
pip install langsmith==0.1.57
```

If local tested python package is successful, need to update package version too.
For example, `lib/shared/file-import-dockerfile`

```
# FROM quay.io/unstructured-io/unstructured:0.11.2
FROM quay.io/unstructured-io/unstructured:0.13.7  # Use the successful version which tested
```

Also need to update `requirements.txt` package version which is fit with tested python package version.
- `lib/shared/layers/common/requirements.txt`
- `lib/shared/file-import-batch-job/requirements.txt`


### Set environment variables

- Need to deploy cdk first
- Create `.env` file to use opensearch, kendra, dynamodb, ...

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

### How to test with AOSS in local

- Default CDK deployment uses private VPC access for AOSS. Also only some lambda can access to data (data access policy)
- Need to change AOSS config
  - Access available from public : private to public 
  - Data access policy (Add IAM user which used in local profile)
- Also need to set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` correctly.


### Local test with mock data

There are sample mock data in `tests/mock-data`. The variable is depends on each AWS account, you must change the value for local testing.


### Frontend app local testing

Check the [guide](https://aws-samples.github.io/aws-genai-llm-chatbot/guide/deploy.html#run-user-interface-locally) for locally run frontend application (React App)


#### How to modify API for frontend

To modify GraphQL API, need to modify `schema.graphql` first.
And use command below to generate `API.ts` file.

```
# From the project root
$ npm run gen   # Check the package.json

# Or you can use codegen directly
$ amplify codegen
```


### If you use `finch` on MacOS to deploy CDK

- Need to increase storage size when there's `no space left on device` error to build container image for file import job.
  - Check the document: https://runfinch.com/docs/managing-finch/macos/disk-management/#disk-size
- Need to use `CDK_DOCKER` env variables when running deployment command.
  - `CDK_DOCKER=finch npx cdk deploy`
  - Check the `scripts/cdk_deploy_finch.sh`


