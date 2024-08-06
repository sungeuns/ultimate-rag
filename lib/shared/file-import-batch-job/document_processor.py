
import os
import json
from typing import List
from PIL import Image

import genai_core.chunks
import genai_core.documents


IMAGE_MIN_SIZE_THRESHOLD = 1024 * 10 # 10KB
IMAGE_WH_MIN_PIXEL_THRESHOLD = 5
IMAGE_WH_RATIO_THRESHOLD = 50

CHAR_LEN_MIN_THRESHOLD = 20
ADD_MD_FORMAT_TABLE = False  # Currently not working well for multi-language

DOC_SUMMARIZATION_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
DOC_SUMMARIZATION_LEN_LIMIT = 25000
DOC_SUMMARIZATION_PROMPT = """
You're an expert at reading and summarizing documentation. 
Summarize the following data in the <document>.
Include as much of the important stuff in your documentation as possible.

Output it within a JSON format below without markdown format:
{{"title": Title of the document, "summary": Summary of the document}}

<document>
{doc_contents}
</document>
"""


class DocumentProcessor:

    def __init__(self, s3_client, bedrock_client, out_bucket, out_key) -> None:
        self.s3_client = s3_client
        self.bedrock_client = bedrock_client
        self.out_bucket = out_bucket
        self.out_prefix = os.path.split(out_key)[0]

    def validate_image(self, file_path):
        file_size = os.path.getsize(file_path)
        if file_size <= IMAGE_MIN_SIZE_THRESHOLD:
            return False
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size

                if width <= IMAGE_WH_MIN_PIXEL_THRESHOLD or height <= IMAGE_WH_MIN_PIXEL_THRESHOLD:
                    return False

                aspect_ratio = max(width / height, height / width)
                if aspect_ratio > IMAGE_WH_RATIO_THRESHOLD:
                    return False

        except Exception as e:
            print(f"Failed to load image: {e}")
            return False

        return True

    def get_llm_result(self, prompt):
    
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature" : 0.1,
                "top_p": 0.5,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            }) 

        response = self.bedrock_client.invoke_model(
            body=body,
            modelId=DOC_SUMMARIZATION_MODEL_ID,
            accept='application/json',
            contentType='application/json')

        response_body = json.loads(response.get("body").read())
        llm_output = response_body.get("content")[0].get("text")
        return llm_output

    def add_doc_summarization(self, workspace: dict, document: dict, docs: List[str]):
        
        try:
            doc_contents = "\n\n".join([doc.page_content for doc in docs])

            print(f"Length of original contents : {len(doc_contents)}")
            if len(doc_contents) > DOC_SUMMARIZATION_LEN_LIMIT:
                print("Too long contents. Truncate the contents ")
                doc_contents = doc_contents[:DOC_SUMMARIZATION_LEN_LIMIT]

            prompt = DOC_SUMMARIZATION_PROMPT.format(
                doc_contents=doc_contents
            )
            
            llm_out = self.get_llm_result(prompt)
            print("-------------- Raw LLM output -------------")
            print(llm_out)

            start_index = llm_out.find('{')
            end_index = llm_out.rfind('}') + 1
            json_str = llm_out[start_index:end_index]
            json_str = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

            print("-------------- Refined LLM output -------------")
            print(json_str)

            data = json.loads(json_str)
            doc_title = data["title"]
            doc_summary = data["summary"]
            workspace_id = workspace["workspace_id"]
            document_id = document["document_id"]

            genai_core.documents.set_complex_document_summary(
                workspace_id, document_id, doc_title, doc_summary)
            
        except Exception as e:
            print(f"Failed to get summarization: {e}")
            return False
            
        return True

    def json_to_markdown_table(self, data):
        # json_str = json_str.replace("\'", "\"")
        # data = json.loads(json_str)
        try:

            max_x = max(item['x'] for item in data) + 1
            max_y = max(item['y'] for item in data) + 1
            
            table = [['' for _ in range(max_x)] for _ in range(max_y)]

            for item in data:
                table[item['y']][item['x']] = item['content']

            markdown_table = []

            header = '| ' + ' | '.join(table[0]) + ' |'
            markdown_table.append(header)

            separator = '| ' + ' | '.join(['---'] * len(table[0])) + ' |'
            markdown_table.append(separator)

            for row in table[1:]:
                markdown_table.append('| ' + ' | '.join(row) + ' |')
            
            return "\n".join(markdown_table)

        except Exception as e:
            print(f"Failed to convert json to table: {e}")
            return False
        
    def add_complex_chunks(self, workspace: dict, document: dict,
                           docs: List[str], local_output_dir: str):
        """
        Element of docs
        - page_content
        - metadata
          - TABLE: table_as_html, table_as_cells
          - IMAGE: image_path
        """
        filenames = os.listdir(local_output_dir)

        chunks = []
        chunk_meta = []
        for page in docs:
            page_text = page.page_content
            metadata = page.metadata

            if ADD_MD_FORMAT_TABLE:
                if "table_as_cells" in metadata:
                    table_markdown = self.json_to_markdown_table(metadata["table_as_cells"])
                    print("********************")
                    print(table_markdown)
                    print("********************")
                    if table_markdown:
                        page_text += "\n" + table_markdown

            chunks.append(page_text)
            
            page_number = metadata["page_number"]

            image_list = []
            if metadata.get("image_path", None):
                for filename in filenames:
                    if filename.startswith(f"figure-{page_number}-") or filename.startswith(f"table-{page_number}-"):
                        target_path = os.path.join(local_output_dir, filename)
                        image_list.append(target_path)
            
            meta = {"table": [], "figure": []}
            # Upload files (image and table) to s3
            for image in image_list:

                # Check image is valid. Delete if it's not valid image
                if not self.validate_image(image):
                    if os.path.isfile(image):
                        os.remove(image)
                        print(f" - Invalid image is deleted: {image}")
                    continue

                filename = os.path.basename(image)
                s3_key = f"{self.out_prefix}/{filename}"
                self.s3_client.upload_file(image, self.out_bucket, s3_key)
                s3_uri = f"s3://{self.out_bucket}/{s3_key}"
                print(f"local_path: {image}, s3_uri: {s3_uri}")

                if "table" in filename:
                    meta["table"].append(s3_uri)
                
                elif "figure" in filename:
                    meta["figure"].append(s3_uri)
            
            chunk_meta.append(meta)

        if len(chunks) != len(chunk_meta):
            raise Exception(f"chunks ({len(chunks)}) chunk_meta ({len(chunk_meta)}) have different length")

        self.split_and_add_complex_chunks(workspace, document, chunks, chunk_meta)

    def split_and_add_complex_chunks(
            self, workspace: dict, document: dict,
            chunks: List[str], chunk_meta: List[object]):
        
        refined_chunks = []
        refined_chunk_meta = []
        text_splitter = genai_core.chunks.get_recursive_text_splitter(workspace)
        
        for i in range(len(chunks)):
            chunk = chunks[i]
            meta = chunk_meta[i]

            split_chunks = text_splitter.split_text(chunk)
            for split_chunk in split_chunks:
                if len(split_chunk) > CHAR_LEN_MIN_THRESHOLD:
                    refined_chunks.append(split_chunk)
                    refined_chunk_meta.append(meta)
                else:
                    print(f" - Skip too short chunk in page {i} : {len(split_chunk)}")

        print(f" - Num of refined chunk : {len(refined_chunks)}")
        print(f" - Num of refined meta : {len(refined_chunk_meta)}")
    
        # indexing with page content
        genai_core.chunks.add_chunks(
            workspace=workspace,
            document=document,
            document_sub_id=None,
            chunks=refined_chunks,
            chunk_complements=None,
            replace=True,
            metadata=refined_chunk_meta
        )

    def add_chunks(self, workspace: dict, document: dict, content: str):
        chunks = genai_core.chunks.split_content(workspace, content)

        genai_core.chunks.add_chunks(
            workspace=workspace,
            document=document,
            document_sub_id=None,
            chunks=chunks,
            chunk_complements=None,
            replace=True,
            metadata=None
        )

    def add_qna_style_contents(self, workspace: dict, document: dict, content):
        questions = []
        answers = []
        for item in content:
            question, answer = item
            questions.append(question)
            answers.append(answer)

        print(f"Number of questions : {len(questions)}")
        print(f"Number of answers : {len(answers)}")

        genai_core.chunks.add_chunks(
            workspace=workspace,
            document=document,
            document_sub_id=None,
            chunks=questions,
            chunk_complements=answers,
            replace=True,
            metadata=None
        )
