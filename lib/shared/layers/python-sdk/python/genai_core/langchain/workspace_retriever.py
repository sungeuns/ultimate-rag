
import genai_core.semantic_search
import genai_core.documents
import genai_core.workspaces

from typing import List
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.schema import BaseRetriever, Document


ADD_DOC_SUMMARY = True
DOC_TOP_K = 3


class WorkspaceRetriever(BaseRetriever):
    workspace_id: str

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        
        workspace = genai_core.workspaces.get_workspace(self.workspace_id)

        result = genai_core.semantic_search.semantic_search(
            self.workspace_id, query, limit=DOC_TOP_K, full_response=False
        )

        doc_cache = {}
        doc_list = []
        for item in result.get("items", []):
            if workspace.get("doc_type") == "COMPLEX" and ADD_DOC_SUMMARY is True:
                doc_id = item["document_id"]

                if doc_id in doc_cache:
                    related_doc = doc_cache[doc_id]
                else:
                    related_doc = genai_core.documents.get_document(self.workspace_id, doc_id)
                    doc_cache[doc_id] = related_doc

                doc_list.append(self._get_document(item,
                        doc_title = related_doc.get("doc_title", None),
                        doc_summary = related_doc.get("doc_summary", None)))
            else:
                doc_list.append(self._get_document(item))

        return doc_list

        # return [self._get_document(item) for item in result.get("items", [])]

    def _get_document(self, item, doc_title=None, doc_summary=None):
        content = item["content"]
        content_complement = item.get("content_complement")

        page_content = content
        if content_complement:
            page_content = content_complement

        if doc_title and doc_summary and ADD_DOC_SUMMARY:
            page_content = f"{doc_title}\n\n{doc_summary}\n\n{page_content}"

        metadata = {
            "chunk_id": item["chunk_id"],
            "workspace_id": item["workspace_id"],
            "document_id": item["document_id"],
            "document_sub_id": item["document_sub_id"],
            "document_type": item["document_type"],
            "document_sub_type": item["document_sub_type"],
            "path": item["path"],
            "title": item["title"],
            "metadata": item["metadata"],
            "score": item["score"],
        }

        if ADD_DOC_SUMMARY:
            if doc_title:
                metadata["doc_title"] = doc_title

            if doc_summary:
                metadata["doc_summary"] = doc_summary

        return Document(page_content=page_content, metadata=metadata)

