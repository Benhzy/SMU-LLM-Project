# EMDB/db.py

import os
import chromadb
from chromadb.utils import embedding_functions
import uuid

num_results =  10000000000000000 # change this value, or we can add something that will change this value to add more results to the retrieval

class db:
    def __init__(self, client_name, EmbeddingModelName="BAAI/bge-m3", device="cpu"): 
        # alternative embedding models: "all-MiniLM-L6-v2" (default in chromadb)
        # there is also gpu embedding support: https://cookbook.chromadb.dev/embeddings/gpu-support/ -- use "ONNXMiniLM_L6_V2", BUT YOU NEED A NEW VERSION.

        self.client_name = client_name
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EmbeddingModelName, device=device
        )
        self.client = self._create_client()
        self.internal_collection = self._create_collection(collection_name="internal-collection")
        self.external_collection = self._create_collection(collection_name="external-collection")

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

    def add_to_internal_collection(self, id, document, metadata=None):
        self.internal_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id] if id else uuid.uuid4()
        )

    def add_to_external_collection(self, id, document, metadata=None):
        self.external_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id] if id else uuid.uuid4()
        )

    def filter_results(result, similarity_threshold=0.7): # this is the result from the query collection functions
        filtered_results = []
        for doc, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            if 1 - distance >= similarity_threshold:
                filtered_results.append((doc, metadata, distance))
        sorted_results = sorted(filtered_results, key=lambda x: x[1].get("case_date", ""), reverse=True)
        return {
            "documents": [item[0] for item in sorted_results],
            "metadatas": [item[1] for item in sorted_results],
            "distances": [item[2] for item in sorted_results]
        }

    def query_internal_collection(self, query_text, tags=None, n_results=num_results, include=["documents", "metadatas", "distances"], similarity_threshold=0.7):
        where_clause = {}
        if tags:
            where_clause["tags"] = {"$in": tags}
        result = self.internal_collection.query(
            query_texts=[query_text], 
            n_results=num_results, 
            include=include,
            where=where_clause,
            #includes are either documents, queries, metadatas, or distances
        )
        return result
    
    def query_external_collection(self, query_text, tags=None, n_results=num_results, include=["documents", "metadatas", "distances"], similarity_threshold=0.7):
        where_clause = {}
        if tags:
            where_clause["tags"] = {"$in": tags}
        result = self.external_collection.query(
            query_texts=[query_text], 
            n_results=num_results, 
            include=include,
            where=where_clause,
            #includes are either documents, queries, metadatas, or distances
        )
        return result

    def query_collection_documents(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_case(query_text, tags, similarity_threshold, include=["documents"])
        return result["documents"]
    
    def query_internal_documents(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_internal_collection(query_text, tags, similarity_threshold, include=["documents"])
        return result["documents"]
    
    def query_external_documents(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_external_collection(query_text, tags, similarity_threshold, include=["documents"])
        return result["documents"]
    
    def query_internal_metadatas(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_internal_collection(query_text, tags, similarity_threshold, include=["documents"])
        return result["metadatas"]
    
    def query_external_metadatas(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_external_collection(query_text, tags, similarity_threshold, include=["metadatas"])
        return result["metadatas"]

    def query_collection_metadatas(self, query_text, tags=None, similarity_threshold=0.7):
        result = self.query_case(query_text, tags, similarity_threshold, include=["metadatas"])
        return result["metadatas"]