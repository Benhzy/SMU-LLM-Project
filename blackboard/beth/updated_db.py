# EMDB/db.py

import os
import onnxruntime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
import uuid

num_results = 5 # change this value, or we can add something that will change this value to add more results to the retrieval

class db:
    def __init__(self, client_name, EmbeddingModelName="BAAI/bge-m3", device="cpu", collection_name="default"): 
        # alternative embedding models: "all-MiniLM-L6-v2" (default in chromadb)
        # there is also gpu embedding support: https://cookbook.chromadb.dev/embeddings/gpu-support/ -- use "ONNXMiniLM_L6_V2", BUT YOU NEED A NEW VERSION.

        self.client_name = client_name
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EmbeddingModelName, device=device
        )
        self.client = self._create_client()
        self.experience_collection = self._create_collection(collection_name=collection_name)

    # CREATES CLIENT AND THEN DATABASE BASED ON NAME OF THE AGENT
    def _create_client(self):
        client_path = os.path.join("db", self.client_name)
        os.makedirs(client_path, exist_ok=True)
        return chromadb.PersistentClient(path=client_path)

    def _create_collection(self, collection_name):
        return self.client.get_or_create_collection(
            name=f"{self.client_name}_{collection_name}",
            embedding_function=self.embedding_fn,
        )

    def add_to_collection(self, id, document, metadata=None):
        self.experience_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id] if id else uuid.uuid4()
        )

    def query_collection(self, query_text, n_results=num_results, include=["documents"]):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=include
            #includes are either documents, queries, metadatas, or distances
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""

    def query_collection_metadatas(self, query_text, n_results=num_results):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=["metadatas"]
        )
        metadatas = result.get("metadatas", [[]])[0]

        # 查找包含 "context" 键的第一个字典
        for metadata in metadatas:
            if "context" in metadata:
                return metadata["context"]

        # 如果没有找到包含 "context" 的字典，返回空字符串
        return ""

    def query_collection_documents(self, query_text, n_results=5):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=["documents"]
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""