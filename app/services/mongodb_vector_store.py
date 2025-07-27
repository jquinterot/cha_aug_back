from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from pymongo.operations import UpdateOne
import numpy as np
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBVectorStore(VectorStore):
    """MongoDB Vector Store with Atlas Vector Search"""
    
    def __init__(
        self,
        collection: Collection,
        embedding: Embeddings,
        index_name: str = "vector_index",
        embedding_key: str = "embedding",
        text_key: str = "text",
        metadata_key: str = "metadata"
    ):
        self.collection = collection
        self.embedding = embedding
        self.index_name = index_name
        self.embedding_key = embedding_key
        self.text_key = text_key
        self.metadata_key = metadata_key
        
        # Create vector search index if it doesn't exist
        self._create_index()
    
    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        database_name: str,
        collection_name: str,
        embedding: Embeddings,
        **kwargs
    ) -> 'MongoDBVectorStore':
        """Create a MongoDBVectorStore from a connection string"""
        client = MongoClient(connection_string)
        db = client[database_name]
        collection = db[collection_name]
        return cls(collection=collection, embedding=embedding, **kwargs)
    
    def _create_index(self):
        """Create a vector search index if it doesn't exist"""
        index_name = f"{self.index_name}_{self.embedding_key}"
        
        # Check if index already exists
        existing_indexes = self.collection.list_indexes()
        index_exists = any(index.get("name") == index_name for index in existing_indexes)
        
        if not index_exists:
            # Create vector search index
            self.collection.create_index(
                [(self.embedding_key, "cosmosSearch")],
                name=index_name,
                cosmosSearchOptions={
                    "kind": "vector-ivf",
                    "numLists": 1,
                    "similarity": "COS",
                    "dimensions": len(self.embedding.embed_query("test"))
                }
            )
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs
    ) -> List[str]:
        """Add texts to the vector store"""
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        # Generate embeddings
        embeddings = self.embedding.embed_documents(texts)
        
        # Prepare documents
        documents = []
        for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            doc = {
                self.text_key: text,
                self.embedding_key: embedding,
                self.metadata_key: metadata or {}
            }
            documents.append(doc)
        
        # Insert documents
        result = self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4, 
        **kwargs
    ) -> List[Document]:
        """Return documents most similar to query"""
        # Generate query embedding
        query_embedding = self.embedding.embed_query(query)
        
        # Vector search pipeline
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": self.embedding_key,
                        "k": k
                    },
                    "returnStoredSource": True
                }
            },
            {"$project": {"_id": 0, "text": f"${self.text_key}", "metadata": f"${self.metadata_key}"}}
        ]
        
        # Execute search
        results = list(self.collection.aggregate(pipeline))
        
        # Convert to Document objects
        docs = [
            Document(
                page_content=result["text"],
                metadata=result.get("metadata", {})
            )
            for result in results
        ]
        
        return docs
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding: Embeddings,
        **kwargs
    ) -> 'MongoDBVectorStore':
        """Create a vector store from documents"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return cls.from_texts(texts, embedding, metadatas=metadatas, **kwargs)
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs
    ) -> 'MongoDBVectorStore':
        """Create a vector store from texts"""
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        # Get or create the vector store
        vector_store = cls(embedding=embedding, **kwargs)
        
        # Add texts
        vector_store.add_texts(texts, metadatas)
        
        return vector_store
