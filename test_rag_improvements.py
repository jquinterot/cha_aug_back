import asyncio
import json
import os
import sys
from typing import List, Dict, Any
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.absolute())
sys.path.append(project_root)

# Set environment variables
os.environ["CHUNK_SIZE"] = "1000"
os.environ["CHUNK_OVERLAP"] = "200"
os.environ["EMBEDDING_MODEL"] = "sentence-transformers/all-mpnet-base-v2"

# Import after setting up environment
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_QUERIES = [
    # ISTQB syllabus queries
    "What is the ISTQB Foundation Level syllabus structure?",
    "What are the main testing principles in ISTQB?",
    "Explain the test process in ISTQB",
    "What is test analysis and design?",
    "What are test techniques in ISTQB?",
    
    # Specific concept queries
    "What is boundary value analysis?",
    "Explain equivalence partitioning",
    "What is state transition testing?",
    "What is decision table testing?",
    "Explain use case testing",
    
    # Process-related queries
    "What is test planning?",
    "How to estimate test effort?",
    "What is test monitoring and control?",
    "Explain test closure activities",
    "What is risk-based testing?",
    
    # Tool-related queries
    "What are test management tools?",
    "What is test automation?",
    "What are static analysis tools?",
    "What is performance testing?",
    "What is security testing?"
]

async def test_rag_queries():
    """Test the RAG system with a variety of queries."""
    # Initialize RAG service with the desired embedding model and index name
    rag_service = RAGService(
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        index_name="vector_index"  # Using the correct index file that contains the documents
    )
    
    results = []
    
    for query in TEST_QUERIES:
        try:
            print(f"\n{'='*80}")
            print(f"QUERY: {query}")
            print(f"{'='*80}")
            
            # Get relevant documents first
            print("\nRELEVANT DOCUMENTS:")
            docs = await rag_service._get_relevant_documents(query, top_k=3)
            for i, doc in enumerate(docs, 1):
                source = doc.get('source', 'unknown')
                is_syllabus = "SYLLABUS" if doc.get('is_syllabus') else ""
                print(f"\nDocument {i} ({is_syllabus}): {source}")
                print(f"Score: {doc.get('score', 0):.4f}")
                print(f"Content: {doc.get('page_content', '')[:300]}...")
            
            # Get RAG response
            print("\nRAG RESPONSE:")
            response = await rag_service.generate_response(query)
            print(f"Answer: {response.answer}")
            print(f"Sources: {response.sources}")
            
            results.append({
                "query": query,
                "answer": response.answer,
                "sources": response.sources,
                "documents": [
                    {
                        "source": doc.get("source"),
                        "is_syllabus": doc.get("is_syllabus", False),
                        "score": float(doc.get("score", 0)),
                        "content_preview": doc.get("page_content", "")[:500]
                    }
                    for doc in docs
                ]
            })
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            results.append({
                "query": query,
                "error": str(e),
                "answer": "",
                "sources": []
            })
    
    # Save results to file
    output_file = "rag_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest results saved to {output_file}")
    return results

if __name__ == "__main__":
    asyncio.run(test_rag_queries())
