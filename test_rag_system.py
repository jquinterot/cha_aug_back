import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pprint import pprint
from dotenv import load_dotenv
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_rag_queries(rag_service: RAGService, queries: List[str]):
    """Test the RAG system with a list of queries and print results."""
    results = {}
    
    for query in queries:
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"QUERY: {query}")
            logger.info(f"{'='*80}")
            
            # Get RAG response - properly await the async method
            response = await rag_service.generate_response(query)
            
            # Format and store results
            results[query] = {
                'answer': response.answer if hasattr(response, 'answer') else 'No answer generated',
                'sources': [{
                    'source': getattr(src, 'source', 'Unknown'),
                    'page': getattr(src, 'page', 'N/A'),
                    'score': f"{getattr(src, 'score', 0):.3f}" if hasattr(src, 'score') else 'N/A'
                } for src in response.sources] if hasattr(response, 'sources') else []
            }
            
            # Print results
            logger.info(f"ANSWER: {response.answer}")
            logger.info("\nSOURCES:")
            for src in response.sources:
                logger.info(f"- {src.get('source', 'Unknown')} (Page: {src.get('page', 'N/A')}, Score: {src.get('score', 0):.3f})")
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}", exc_info=True)
            results[query] = {
                'error': str(e),
                'answer': None,
                'sources': []
            }
    
    return results

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Define test queries
    test_queries = [
        "What is the ISTQB Foundation Level certification?",
        "What are the key differences between black-box and white-box testing?",
        "Explain the test process according to the ISTQB syllabus.",
        "What are the main principles of testing?",
        "How does risk-based testing work?",
        "What is the difference between verification and validation?",
        "Describe the test levels in the ISTQB framework.",
        "What is the purpose of test design techniques?",
        "Explain the concept of test coverage.",
        "What are the characteristics of good testing?"
    ]
    
    # Run tests
    logger.info("Starting RAG system tests...")
    results = await test_rag_queries(rag_service, test_queries)
    
    # Save results to file
    output_file = "rag_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\nTest results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
