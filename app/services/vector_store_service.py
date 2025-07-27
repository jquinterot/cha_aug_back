from typing import List, Optional, Dict, Any
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    from langchain_community.vectorstores import FAISS
except ImportError:
    # Fallback for older versions
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.docstore.document import Document
    from langchain.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Constants
VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vector_store')
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

class VectorStoreService:
    def __init__(
        self,
        model_name: Optional[str] = None,
        index_name: Optional[str] = None
    ):
        # Load configuration from environment variables with defaults
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.index_name = index_name or os.getenv("VECTOR_INDEX_NAME", "default_index")
        
        # Initialize embeddings with the configured model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        
        # Initialize FAISS vector store
        self.vector_store = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load the FAISS vector store from disk or create a new one"""
        vector_store_path = os.path.join(VECTOR_STORE_DIR, f"{self.index_name}.pkl")
        
        if os.path.exists(vector_store_path):
            # Load existing vector store
            with open(vector_store_path, "rb") as f:
                self.vector_store = pickle.load(f)
        else:
            # Create a new empty vector store
            self.vector_store = FAISS.from_texts(
                ["Initial document"],  # Dummy document to initialize
                self.embeddings
            )
            self._save_vector_store()
    
    def _save_vector_store(self):
        """Save the FAISS vector store to disk"""
        if self.vector_store is None:
            return
            
        vector_store_path = os.path.join(VECTOR_STORE_DIR, f"{self.index_name}.pkl")
        with open(vector_store_path, "wb") as f:
            pickle.dump(self.vector_store, f)
    
    def create_vector_store(self, documents: List[Document]):
        """Create or update the vector store with new documents"""
        if not documents:
            return self
            
        # Convert documents to texts and metadatas
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        if self.vector_store is None:
            # Create new vector store
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
        else:
            # Add to existing vector store
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
        
        # Save the updated vector store
        self._save_vector_store()
        return self
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            return []
            
        # Perform similarity search
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Convert to list of Document objects
        documents = []
        for doc, score in docs_and_scores:
            # Add similarity score to metadata
            doc.metadata["score"] = float(score)
            documents.append(doc)
            
        return documents
