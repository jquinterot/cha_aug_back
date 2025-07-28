"""
Test script to verify polite responses from the RAG service.
"""
import asyncio
import httpx
import json

async def test_polite_response():
    """Test the RAG service with polite response formatting."""
    base_url = "http://localhost:8000"
    
    # Test queries
    test_queries = [
        "What is the capital of Zyxoria?",
        "Tell me about Zyxoria's national dish",
        "What language do they speak in Zyxoria?",
        "What is the currency of Zyxoria?",
        "Tell me about something not in the knowledge base"
    ]
    
    async with httpx.AsyncClient() as client:
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Testing query: {query}")
            print("-" * 40)
            
            # Call the RAG query endpoint
            response = await client.post(
                f"{base_url}/api/v1/rag/query",
                json={"query": query},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result['answer']}")
                print(f"\nSources:")
                for i, source in enumerate(result.get('sources', [])[:2], 1):
                    print(f"  {i}. From: {source.get('source', 'Unknown')}")
                    if 'score' in source.get('metadata', {}):
                        print(f"     Score: {source['metadata']['score']:.3f}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
            
            # Add a small delay between requests
            await asyncio.sleep(1)

if __name__ == "__main__":
    print("Testing RAG service with polite responses...")
    asyncio.run(test_polite_response())
