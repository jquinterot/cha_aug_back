import sys
import feedparser
import ssl
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Handle SSL certificate verification
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def parse_bbc_rss(feed_url: str = "http://feeds.bbci.co.uk/news/world/rss.xml") -> List[Dict[str, Any]]:
    """Parse BBC RSS feed and return structured data."""
    print(f"Fetching BBC World News RSS feed from: {feed_url}")
    
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    
    if feed.bozo and feed.bozo_exception:
        print(f"Error parsing feed: {feed.bozo_exception}")
        return []
    
    print(f"\nFeed Title: {feed.feed.get('title', 'No title')}")
    print(f"Last Updated: {feed.feed.get('updated', 'N/A')}")
    print(f"Number of entries: {len(feed.entries)}\n")
    
    # Process entries
    articles = []
    for i, entry in enumerate(feed.entries[:5], 1):  # Limit to 5 articles
        article = {
            'title': entry.get('title', 'No title'),
            'link': entry.get('link', '#'),
            'published': entry.get('published', 'N/A'),
            'summary': entry.get('summary', 'No summary available'),
            'source': 'BBC World News',
            'content': f"{entry.get('title', '')}\n\n{entry.get('summary', '')}"
        }
        articles.append(article)
        
        # Print article info
        print(f"{i}. {article['title']}")
        print(f"   Published: {article['published']}")
        print(f"   Link: {article['link']}")
        print("   Summary:", " ".join(article['summary'].split()[:30]) + "...")
        print("-" * 80)
    
    return articles

def test_rss_loading():
    """Test loading and processing BBC RSS feed."""
    rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    
    try:
        articles = parse_bbc_rss(rss_url)
        
        if not articles:
            print("No articles found in the feed.")
            return
        
        # Test with our document processor
        from app.services.document_service import DocumentProcessor
        
        print("\n" + "="*80)
        print("Testing with DocumentProcessor")
        print("="*80)
        
        processor = DocumentProcessor()
        
        # Convert articles to Document objects
        from langchain_core.documents import Document
        
        documents = [
            Document(
                page_content=article['content'],
                metadata={
                    'source': article['link'],
                    'title': article['title'],
                    'published': article['published'],
                    'type': 'news_article'
                }
            )
            for article in articles
        ]
        
        # Process the documents
        chunks = processor.split_documents(documents)
        
        print(f"\nSplit {len(documents)} articles into {len(chunks)} chunks.")
        
        # Show first chunk
        if chunks:
            print("\nFirst chunk preview:")
            print("-" * 50)
            print(chunks[0].page_content[:300] + "...")
            print("-" * 50)
            print(f"Source: {chunks[0].metadata.get('source', 'Unknown')}")
            print(f"Title: {chunks[0].metadata.get('title', 'No title')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rss_loading()
