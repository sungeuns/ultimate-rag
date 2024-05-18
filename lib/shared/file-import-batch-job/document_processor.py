
import os
from typing import List

import genai_core.chunks


class DocumentProcessor:

    def __init__(self, s3_client, out_bucket, out_key) -> None:
        self.s3_client = s3_client
        self.out_bucket = out_bucket
        self.out_prefix = os.path.split(out_key)[0]

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
            chunks.append(page_text)
            metadata = page.metadata
            page_number = metadata["page_number"]

            image_list = []
            if metadata.get("image_path", None):
                for filename in filenames:
                    if filename.startswith(f"figure-{page_number}") or filename.startswith(f"table-{page_number}"):
                        target_path = os.path.join(local_output_dir, filename)
                        image_list.append(target_path)
            
            meta = {"table": [], "figure": []}
            # Upload files (image and table) to s3
            for image in image_list:
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

        # chunks = genai_core.chunks.split_content(workspace, content)

        # indexing with page content
        genai_core.chunks.add_chunks(
            workspace=workspace,
            document=document,
            document_sub_id=None,
            chunks=chunks,
            chunk_complements=None,
            replace=True,
            metadata=chunk_meta
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