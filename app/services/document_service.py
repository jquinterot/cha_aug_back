from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader
)
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentProcessor:
    def __init__(
        self, 
        chunk_size: Optional[int] = None, 
        chunk_overlap: Optional[int] = None,
        model_name: Optional[str] = None
    ):
        # Load configuration from environment variables with defaults
        self.chunk_size = int(os.getenv("CHUNK_SIZE", chunk_size or 1000))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", chunk_overlap or 200))
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def load_documents(self, file_path: str = None, urls: List[str] = None) -> List[Document]:
        """Load documents from file path or URLs"""
        documents = []
        
        if file_path:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
            
        if urls:
            for url in urls:
                loader = WebBaseLoader(url)
                documents.extend(loader.load())
                
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
