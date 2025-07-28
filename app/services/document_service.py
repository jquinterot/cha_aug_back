from typing import List, Optional, Union, Dict, Any
from pathlib import Path
import json
import yaml
import requests
from urllib.parse import urlparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader, 
    UnstructuredMarkdownLoader, JSONLoader, WebBaseLoader, UnstructuredURLLoader
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

    def _load_json_file(self, file_path: str) -> List[Document]:
        """Load and parse JSON file into documents."""
        try:
            loader = JSONLoader(
                file_path=file_path,
                jq_schema='.',
                text_content=False
            )
            return loader.load()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")

    def _load_yaml_file(self, file_path: str) -> List[Document]:
        """Load and parse YAML file into documents."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if not data:
                    return []
                # Convert YAML content to a string representation
                content = yaml.dump(data, default_flow_style=False)
                return [Document(page_content=content, metadata={"source": file_path})]
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

    def _load_url_content(self, url: str) -> List[Document]:
        """Load content from a URL."""
        try:
            # First try WebBaseLoader for web pages
            if any(url.endswith(ext) for ext in ['.pdf', '.txt', '.md', '.json', '.yaml', '.yml']):
                # For direct file URLs, use appropriate loader
                if url.endswith('.pdf'):
                    return PyPDFLoader(url).load()
                elif url.endswith(('.yaml', '.yml')):
                    response = requests.get(url)
                    response.raise_for_status()
                    data = yaml.safe_load(response.text)
                    return [Document(page_content=yaml.dump(data), metadata={"source": url})]
                elif url.endswith('.json'):
                    response = requests.get(url)
                    response.raise_for_status()
                    return [Document(page_content=response.text, metadata={"source": url})]
                else:
                    return TextLoader(url).load()
            else:
                # For web pages, use WebBaseLoader
                return WebBaseLoader(url).load()
        except Exception as e:
            raise ValueError(f"Error loading URL {url}: {str(e)}")

    def load_documents(self, file_path: str = None, urls: List[str] = None) -> List[Document]:
        """
        Load documents from file path or URLs.
        
        Args:
            file_path: Path to a file (supports .pdf, .txt, .md, .json, .yaml, .yml)
            urls: List of URLs to load content from
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if file_path:
            file_path = str(Path(file_path).absolute())
            file_ext = Path(file_path).suffix.lower()
            
            try:
                if file_ext == '.pdf':
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file_ext == '.json':
                    documents.extend(self._load_json_file(file_path))
                elif file_ext in ['.yaml', '.yml']:
                    documents.extend(self._load_yaml_file(file_path))
                elif file_ext == '.md':
                    documents.extend(UnstructuredMarkdownLoader(file_path).load())
                elif file_ext == '.docx':
                    documents.extend(Docx2txtLoader(file_path).load())
                else:
                    # Default to text loader for other file types
                    documents.extend(TextLoader(file_path, encoding='utf-8').load())
            except Exception as e:
                print(f"Error loading file {file_path}: {str(e)}")
                raise
            
        if urls:
            for url in urls:
                try:
                    documents.extend(self._load_url_content(url))
                except Exception as e:
                    print(f"Error loading URL {url}: {str(e)}")
                    continue
                
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
