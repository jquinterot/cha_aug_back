from typing import List, Optional, Union, Dict, Any, Tuple
from pathlib import Path
import json
import yaml
import re
import requests
from urllib.parse import urlparse
from langchain_text_splitters import RecursiveCharacterTextSplitter, RecursiveJsonSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader, 
    UnstructuredMarkdownLoader, JSONLoader, WebBaseLoader, UnstructuredURLLoader,
    UnstructuredPDFLoader, PyPDFium2Loader
)
from langchain_core.documents import Document
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Common phrases to remove from documents
BOILERPLATE_PHRASES = [
    r'istqb®',
    r'copyright ©',
    r'all rights reserved',
    r'document responsibility:',
    r'this document may be copied in its entirety',
    r'sample exam',
    r'these questions cannot be used as-is in any official examination',
    r'istqb® foundation level',
    r'istqb® examination working group',
    r'acknowledgements',
    r'version \d+\.\d+',
    r'page \d+ of \d+',
    r'document version',
    r'confidential',
    r'proprietary',
    r'internal use only'
]

# Common headers/footers to remove
HEADER_FOOTER_PATTERNS = [
    r'^\s*\d+\s*$',  # Page numbers on their own line
    r'^\s*[ivx]+\s*$',  # Roman numerals
    r'^\s*[a-z]\s*$',  # Single letters (often in headers)
    r'^\s*chapter \d+\s*$',  # Chapter headers
    r'^\s*section [\d\.]+\s*$',  # Section headers
]

def clean_text(text: str) -> str:
    """Clean and preprocess text content."""
    if not text:
        return ""
    
    # Remove common boilerplate
    for phrase in BOILERPLATE_PHRASES:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    
    # Remove headers/footers
    for pattern in HEADER_FOOTER_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

class DocumentProcessor:
    def __init__(
        self, 
        chunk_size: Optional[int] = None, 
        chunk_overlap: Optional[int] = None,
        model_name: Optional[str] = None,
        use_structured_parsing: bool = True
    ):
        # Load configuration from environment variables with defaults
        self.chunk_size = int(os.getenv("CHUNK_SIZE", chunk_size or 600))  # Slightly larger chunks for better context
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", chunk_overlap or 150))  # Increased overlap for better context
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
        self.use_structured_parsing = use_structured_parsing
        
        # Initialize text splitter with better handling for technical content
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=True,
            separators=[
                "\n\n\n",  # Triple newlines (major section breaks)
                "\n\n",    # Double newlines
                "\n",      # Single newlines
                " ",        # Spaces
                "",         # No separator (fallback)
            ]
        )

    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load and process PDF files with improved extraction."""
        try:
            # Try PyPDFium2 first for better text extraction
            try:
                loader = PyPDFium2Loader(file_path)
                docs = loader.load()
            except Exception as e:
                logger.warning(f"PyPDFium2 failed, falling back to PyPDFLoader: {str(e)}")
                loader = PyPDFLoader(file_path, extract_images=False)
                docs = loader.load()
            
            # Clean and process each document
            processed_docs = []
            for doc in docs:
                # Clean the content
                cleaned_content = clean_text(doc.page_content)
                if not cleaned_content.strip():
                    continue
                    
                # Update document with cleaned content and metadata
                doc.page_content = cleaned_content
                doc.metadata.update({
                    "source": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_type": "pdf",
                    "page": doc.metadata.get("page", 0) + 1,  # 1-based page numbers
                    "last_updated": datetime.utcnow().isoformat()
                })
                
                # Only include documents with sufficient content
                if len(cleaned_content.split()) > 10:  # At least 10 words
                    processed_docs.append(doc)
            
            return processed_docs
            
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    def _load_json_file(self, file_path: str) -> List[Document]:
        """Load and parse JSON file into documents with better handling."""
        try:
            # First try standard JSON loader
            try:
                loader = JSONLoader(
                    file_path=file_path,
                    jq_schema='.',
                    text_content=False
                )
                docs = loader.load()
            except Exception as e:
                logger.warning(f"Standard JSON loader failed, trying fallback: {str(e)}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                content = json.dumps(data, indent=2)
                docs = [Document(page_content=content, metadata={"source": file_path})]
            
            # Clean and process documents
            processed_docs = []
            for doc in docs:
                cleaned_content = clean_text(doc.page_content)
                if cleaned_content.strip():
                    doc.page_content = cleaned_content
                    doc.metadata.update({
                        "source": file_path,
                        "file_name": os.path.basename(file_path),
                        "file_type": "json",
                        "last_updated": datetime.utcnow().isoformat()
                    })
                    processed_docs.append(doc)
            
            return processed_docs
            
        except Exception as e:
            raise ValueError(f"Invalid JSON file {file_path}: {str(e)}")

    def _load_yaml_file(self, file_path: str) -> List[Document]:
        """Load and parse YAML file into documents with better handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if not data:
                    return []
                
                # Convert YAML content to a clean string representation
                content = yaml.dump(data, default_flow_style=False, sort_keys=False)
                cleaned_content = clean_text(content)
                
                if not cleaned_content.strip():
                    return []
                    
                return [Document(
                    page_content=cleaned_content,
                    metadata={
                        "source": file_path,
                        "file_name": os.path.basename(file_path),
                        "file_type": "yaml",
                        "last_updated": datetime.utcnow().isoformat()
                    }
                )]
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing YAML file {file_path}: {str(e)}")

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
