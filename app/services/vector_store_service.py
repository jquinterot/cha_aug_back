from typing import List, Optional, Dict, Any, Union, Iterable
import os
import pickle
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Try to find any .pkl file in the vector store directory
        pkl_files = [f for f in os.listdir(VECTOR_STORE_DIR) if f.endswith('.pkl')]
        
        if not pkl_files:
            logger.info("No vector store files found. Creating a new one.")
            self._create_new_vector_store()
            return
            
        # Try to load the specified index if it exists
        specified_index = f"{self.index_name}.pkl"
        vector_store_path = os.path.join(VECTOR_STORE_DIR, specified_index)
        
        # If the specified index doesn't exist, use the first available one
        if not os.path.exists(vector_store_path):
            logger.warning(f"Specified index {specified_index} not found. Using {pkl_files[0]} instead.")
            vector_store_path = os.path.join(VECTOR_STORE_DIR, pkl_files[0])
            
        try:
            logger.info(f"Loading vector store from {vector_store_path}")
            with open(vector_store_path, "rb") as f:
                self.vector_store = pickle.load(f)
                
            if hasattr(self.vector_store, 'index') and hasattr(self.vector_store.index, 'ntotal'):
                logger.info(f"Vector store loaded with {self.vector_store.index.ntotal} vectors")
            else:
                logger.warning("Vector store loaded but unable to determine number of vectors")
                
            # If we loaded a different file than specified, update the index name
            actual_index = os.path.basename(vector_store_path).replace('.pkl', '')
            if actual_index != self.index_name:
                logger.info(f"Using index: {actual_index} (originally requested: {self.index_name})")
                self.index_name = actual_index
                
        except Exception as e:
            logger.error(f"Error loading vector store from {vector_store_path}: {str(e)}")
            logger.info("Creating a new vector store due to loading error")
            self._create_new_vector_store()
            
    def _create_new_vector_store(self):
        """Create a new empty vector store"""
        logger.info("Creating new vector store")
        self.vector_store = FAISS.from_texts(
            ["Initial document"],  # Dummy document to initialize
            self.embeddings,
            metadatas=[{"source": "system", "type": "initialization"}]
        )
        self._save_vector_store()
    
    def _save_vector_store(self):
        """Save the FAISS vector store to disk"""
        if self.vector_store is None:
            logger.warning("Cannot save: vector store is None")
            return False
            
        try:
            # Ensure the vector store directory exists
            os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
            
            # Create the full path for the vector store file
            vector_store_path = os.path.join(VECTOR_STORE_DIR, f"{self.index_name}.pkl")
            temp_path = f"{vector_store_path}.tmp"
            
            logger.info(f"Saving vector store to {vector_store_path}")
            
            # Save to temporary file first
            with open(temp_path, "wb") as f:
                pickle.dump(self.vector_store, f)
            
            # Ensure the file was written
            if not os.path.exists(temp_path):
                raise IOError(f"Failed to write to temporary file: {temp_path}")
                
            # Atomic rename on POSIX systems
            if os.path.exists(vector_store_path):
                os.replace(temp_path, vector_store_path)
            else:
                os.rename(temp_path, vector_store_path)
            
            # Verify the file was saved
            if not os.path.exists(vector_store_path):
                raise IOError(f"Failed to save vector store to {vector_store_path}")
                
            logger.info(f"Successfully saved vector store to {vector_store_path}")
            logger.info(f"Vector store info: {self.vector_store}")
            
            # Log some statistics if available
            if hasattr(self.vector_store, 'index') and hasattr(self.vector_store.index, 'ntotal'):
                logger.info(f"Vector store contains {self.vector_store.index.ntotal} vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}", exc_info=True)
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {str(cleanup_error)}")
            return False
    
    def add_documents(self, documents: Union[Document, List[Document], Iterable[Document]]) -> None:
        """Add documents to the vector store.
        
        Args:
            documents: Single document or list/iterable of documents to add
        """
        if not documents:
            logger.warning("No documents provided to add_documents")
            return
            
        # Convert single document to list
        if isinstance(documents, Document):
            documents = [documents]
            
        # Ensure we have a list
        documents = list(documents)
        
        if not documents:
            logger.warning("No valid documents to add")
            return
            
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            # Convert documents to texts and metadatas
            texts = []
            metadatas = []
            
            for doc in documents:
                if not isinstance(doc, Document):
                    logger.warning(f"Skipping invalid document type: {type(doc)}")
                    continue
                    
                if not doc.page_content.strip():
                    logger.warning("Skipping empty document")
                    continue
                    
                # Ensure metadata is a dictionary
                if not hasattr(doc, 'metadata') or not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                
                # Add source if not present
                if 'source' not in doc.metadata:
                    doc.metadata['source'] = 'unknown'
                    
                texts.append(doc.page_content)
                metadatas.append(doc.metadata)
            
            if not texts:
                logger.warning("No valid texts to add after processing")
                return
                
            if self.vector_store is None:
                # Create new vector store
                self.vector_store = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Created new vector store with {len(texts)} documents")
            else:
                # Add documents to existing store
                self.vector_store.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    embedding=self.embeddings
                )
                logger.info(f"Added {len(texts)} documents to existing vector store")
            
            # Save the updated vector store
            self.save()
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def save(self) -> bool:
        """Save the current state of the vector store to disk.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        return self._save_vector_store()
    
    def create_vector_store(self, documents: List[Document]):
        """Create or update the vector store with new documents
        
        Note: Prefer using add_documents() for incremental updates
        """
        if not documents:
            logger.warning("No documents provided to create_vector_store")
            return self
            
        logger.info(f"Creating/updating vector store with {len(documents)} documents")
            
        try:
            # Convert documents to texts and metadatas
            texts = []
            metadatas = []
            
            for doc in documents:
                if not isinstance(doc, Document):
                    logger.warning(f"Skipping invalid document type: {type(doc)}")
                    continue
                    
                if not doc.page_content.strip():
                    logger.warning("Skipping empty document")
                    continue
                    
                # Ensure metadata is a dictionary
                if not hasattr(doc, 'metadata') or not isinstance(doc.metadata, dict):
                    doc.metadata = {}
                
                # Add source if not present
                if 'source' not in doc.metadata:
                    doc.metadata['source'] = 'unknown'
                    
                texts.append(doc.page_content)
                metadatas.append(doc.metadata)
            
            if not texts:
                logger.warning("No valid texts to process")
                return self
            
            # Create a new index with the provided documents
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Created vector store with {len(texts)} documents")
            
            # Save the updated vector store
            self.save()
            return self
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """Search for similar documents with enhanced scoring and filtering.
        
        Args:
            query: The query string to search for
            k: Maximum number of results to return
            filter_dict: Optional dictionary of metadata filters
            score_threshold: Optional maximum score threshold (lower is better)
            
        Returns:
            List of matching Document objects with scores in metadata
        """
        if self.vector_store is None:
            logger.warning("Vector store not initialized")
            return []
            
        try:
            # Increase k to get more results for better filtering
            fetch_k = min(k * 3, 50)  # Get more results but cap at 50
            
            # Perform similarity search with scores
            docs_and_scores = self.vector_store.similarity_search_with_score(
                query, 
                k=fetch_k,
                filter=filter_dict
            )
            
            if not docs_and_scores:
                logger.info("No results found in similarity search")
                return []
            
            # Convert to list of Document objects with scores
            documents = []
            seen_sources = set()
            
            for doc, score in docs_and_scores:
                # Skip documents with very low scores
                if score_threshold is not None and score > score_threshold:
                    logger.debug(f"Skipping document with score {score} > {score_threshold}")
                    continue
                    
                # Add similarity score to metadata
                doc.metadata["score"] = float(score)
                
                # Skip duplicate sources if needed
                source = doc.metadata.get("source", "")
                if source in seen_sources:
                    logger.debug(f"Skipping duplicate source: {source}")
                    continue
                    
                seen_sources.add(source)
                documents.append(doc)
                
                # Return only the top k unique documents
                if len(documents) >= k:
                    break
            
            logger.info(f"Returning {len(documents)} documents from similarity search")
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}", exc_info=True)
            return []
            
    async def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[tuple[Document, float]]:
        """Search for similar documents and return them with their similarity scores.
        
        This is an async version that matches the interface expected by RAGService.
        
        Args:
            query: The query string to search for
            k: Maximum number of results to return
            filter_dict: Optional dictionary of metadata filters
            score_threshold: Optional maximum score threshold (lower is better)
            
        Returns:
            List of tuples containing (Document, score) pairs
        """
        if self.vector_store is None:
            logger.warning("Vector store not initialized")
            return []
            
        try:
            # Perform similarity search with scores
            docs_and_scores = self.vector_store.similarity_search_with_score(
                query, 
                k=k,
                filter=filter_dict
            )
            
            if not docs_and_scores:
                logger.info("No results found in similarity search with scores")
                return []
                
            # Filter by score threshold if provided
            if score_threshold is not None:
                filtered_results = [
                    (doc, float(score)) 
                    for doc, score in docs_and_scores 
                    if score <= score_threshold
                ]
                logger.info(f"Filtered from {len(docs_and_scores)} to {len(filtered_results)} results with score <= {score_threshold}")
                return filtered_results
                
            # Convert scores to float for consistency
            return [(doc, float(score)) for doc, score in docs_and_scores]
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {str(e)}", exc_info=True)
            return []
