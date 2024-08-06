import os
import time
import boto3
import pandas as pd
from io import StringIO
import genai_core.types
import genai_core.documents
import genai_core.workspaces
import genai_core.aurora.create

# from langchain.document_loaders import S3FileLoader
from langchain_community.document_loaders.s3_file import S3FileLoader

from document_processor import DocumentProcessor


DOC_TYPE_NORMAL = "NORMAL"
DOC_TYPE_COMPLEX = "COMPLEX"
DOC_TYPE_COMPLEX_PDF_SUMMARIZATION = True


WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
DOCUMENT_ID = os.environ.get("DOCUMENT_ID")
INPUT_BUCKET_NAME = os.environ.get("INPUT_BUCKET_NAME")
INPUT_OBJECT_KEY = os.environ.get("INPUT_OBJECT_KEY")
PROCESSING_BUCKET_NAME = os.environ.get("PROCESSING_BUCKET_NAME")
PROCESSING_OBJECT_KEY = os.environ.get("PROCESSING_OBJECT_KEY")


def main():
    s3_client = boto3.client("s3")
    bedrock_client = boto3.client("bedrock-runtime")
    local_output_dir = os.path.join("outputs", DOCUMENT_ID)
    doc_processor = DocumentProcessor(
        s3_client, bedrock_client, PROCESSING_BUCKET_NAME, PROCESSING_OBJECT_KEY)

    print("Starting file converter batch job")
    print("Workspace ID: {}".format(WORKSPACE_ID))
    print("Document ID: {}".format(DOCUMENT_ID))
    print("Input bucket name: {}".format(INPUT_BUCKET_NAME))
    print("Input object key: {}".format(INPUT_OBJECT_KEY))
    print("Output bucket name: {}".format(PROCESSING_BUCKET_NAME))
    print("Output object key: {}".format(PROCESSING_OBJECT_KEY))

    workspace = genai_core.workspaces.get_workspace(WORKSPACE_ID)
    if not workspace:
        raise genai_core.types.CommonError(f"Workspace {WORKSPACE_ID} does not exist")
    
    doc_type = workspace.get("doc_type", DOC_TYPE_NORMAL)
    if doc_type not in [DOC_TYPE_NORMAL, DOC_TYPE_COMPLEX]:
        doc_type = DOC_TYPE_NORMAL

    print(f"Workspace Doc Type: {doc_type}")

    document = genai_core.documents.get_document(WORKSPACE_ID, DOCUMENT_ID)
    if not document:
        raise genai_core.types.CommonError(
            f"Document {WORKSPACE_ID}/{DOCUMENT_ID} does not exist"
        )
    
    if doc_type == DOC_TYPE_COMPLEX:
        os.makedirs(local_output_dir, exist_ok=True)

    try:
        extension = os.path.splitext(INPUT_OBJECT_KEY)[-1].lower()
        if extension == ".txt":
            object = s3_client.get_object(
                Bucket=INPUT_BUCKET_NAME, Key=INPUT_OBJECT_KEY
            )
            content = object["Body"].read().decode("utf-8")

        elif extension == ".csv":
            qa_list = extract_qa_from_csv(s3_client)
            if not qa_list:
                content = load_document_single_page()                
                upload_extracted_content(s3_client, content)
                doc_processor.add_chunks(workspace, document, content)
            else:
                print(f"Number of QnA set : {len(qa_list)}")
                doc_processor.add_qna_style_contents(workspace, document, qa_list)
        else:
            """
            S3FileLoder
            - https://api.python.langchain.com/en/latest/_modules/langchain_community/document_loaders/s3_file.html#S3FileLoader 

            Unstructured partition
            - https://unstructured-io.github.io/unstructured/core/partition.html

            partition_pdf
            - https://docs.unstructured.io/open-source/core-functionality/partitioning#partition-pdf
            
            """
            if doc_type == DOC_TYPE_NORMAL:
                content = load_document_single_page()
                upload_extracted_content(s3_client, content)
                doc_processor.add_chunks(workspace, document, content)

            elif doc_type == DOC_TYPE_COMPLEX:
                
                # Currently it does not working
                ocr_languages = ["eng"]
                # if "korean" in workspace["languages"]:
                #     ocr_languages.append("kor")

                unstructured_params = {
                    "strategy": "hi_res",
                    "extract_images_in_pdf": True,
                    "extract_image_block_types": ["Image", "Table"],
                    "extract_image_block_to_payload": False,
                    "extract_image_block_output_dir": f"./{local_output_dir}",
                    "include_page_breaks": True,
                    "languages": ocr_languages,
                }

                print(f"unstructured.io parameters : {unstructured_params}")

                loader = S3FileLoader(
                    bucket=INPUT_BUCKET_NAME,
                    key=INPUT_OBJECT_KEY,
                    mode="paged",
                    **unstructured_params)
            
                start_time = time.time()
                
                # docs = loader.load()
                # print(f"Number of pages : {len(docs)}")

                # 테스트 결과 lazy_load 사용해도 속도/메모리 이득이 없어 보임.
                doc_iterator = loader.lazy_load()
                docs = []
                for doc in doc_iterator:
                    docs.append(doc)

                extraction_time = time.time()
                print(f"Complex document extarction time: {extraction_time - start_time} sec")

                # PDF 문서이면서 Complex type 의 경우 문서 자체의 정보도 분석함.
                if extension == ".pdf" and DOC_TYPE_COMPLEX_PDF_SUMMARIZATION:
                    doc_processor.add_doc_summarization(workspace, document, docs)
                    print("Document summarization process ...")

                doc_processor.add_complex_chunks(workspace, document, docs, local_output_dir)

                indexing_time = time.time()
                print(f"Summarization/Indexing is finished: {indexing_time - extraction_time} sec")
            else:
                raise Exception(f"Unknown document type: {doc_type}")            
    except Exception as error:
        genai_core.documents.set_status(WORKSPACE_ID, DOCUMENT_ID, "error")
        print(error)
        raise error


def extract_qa_from_csv(s3_client):
    # question, answer
    object = s3_client.get_object(Bucket=INPUT_BUCKET_NAME, Key=INPUT_OBJECT_KEY)
    content = object["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(content))
    if 'question' not in df.columns or 'answer' not in df.columns:
        return False
    result = df[['question', 'answer']].values.tolist()
    return result


def load_document_single_page():
    unstructured_params = {
        "strategy": "fast"
    }
    loader = S3FileLoader(
        bucket=INPUT_BUCKET_NAME,
        key=INPUT_OBJECT_KEY,
        mode="single",
        **unstructured_params)

    docs = loader.load()
    content = docs[0].page_content
    return content


def upload_extracted_content(s3_client, content):
    if (
        INPUT_BUCKET_NAME != PROCESSING_BUCKET_NAME
        and INPUT_OBJECT_KEY != PROCESSING_OBJECT_KEY
    ):
        s3_client.put_object(
            Bucket=PROCESSING_BUCKET_NAME, Key=PROCESSING_OBJECT_KEY, Body=content
        )


if __name__ == "__main__":
    main()
