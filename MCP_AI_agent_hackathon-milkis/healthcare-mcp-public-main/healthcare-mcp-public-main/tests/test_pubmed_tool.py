import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.pubmed_tool import PubMedTool

async def test_pubmed_search():
    """Test the PubMed search functionality"""
    print("\n=== Testing PubMed Search ===")
    
    # Initialize the tool
    tool = PubMedTool()
    
    # Test searching for a medical topic
    print("\nSearching for 'diabetes treatment'...")
    result = await tool.search_literature("diabetes treatment", 5)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Query: {result.get('query', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show articles
    articles = result.get('articles', [])
    print(f"Returned {len(articles)} articles:")
    
    for i, article in enumerate(articles):
        print(f"\n{i+1}. {article.get('title', 'No title')}")
        
        # Show authors (limited to first 3)
        authors = article.get('authors', [])
        if authors:
            print(f"   Authors: ", end="")
            if len(authors) <= 3:
                print(", ".join(authors))
            else:
                print(f"{', '.join(authors[:3])} et al.")
        
        # Show journal and date
        print(f"   Journal: {article.get('journal', 'Unknown')}")
        print(f"   Published: {article.get('publication_date', 'Unknown')}")
        print(f"   URL: {article.get('abstract_url', '')}")
    
    # Test searching with date range
    print("\nSearching for 'covid vaccine' in the last 2 years...")
    result = await tool.search_literature("covid vaccine", 3, "2")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Query: {result.get('query', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show articles
    articles = result.get('articles', [])
    print(f"Returned {len(articles)} articles:")
    
    for i, article in enumerate(articles):
        print(f"\n{i+1}. {article.get('title', 'No title')}")
        
        # Show authors (limited to first 3)
        authors = article.get('authors', [])
        if authors:
            print(f"   Authors: ", end="")
            if len(authors) <= 3:
                print(", ".join(authors))
            else:
                print(f"{', '.join(authors[:3])} et al.")
        
        # Show journal and date
        print(f"   Journal: {article.get('journal', 'Unknown')}")
        print(f"   Published: {article.get('publication_date', 'Unknown')}")
        print(f"   URL: {article.get('abstract_url', '')}")
    
    # Test with more specific medical query
    print("\nSearching for 'hypertension randomized controlled trial'...")
    result = await tool.search_literature("hypertension randomized controlled trial", 3)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Query: {result.get('query', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show articles
    articles = result.get('articles', [])
    print(f"Returned {len(articles)} articles:")
    
    for i, article in enumerate(articles):
        print(f"\n{i+1}. {article.get('title', 'No title')}")
        
        # Show authors (limited to first 3)
        authors = article.get('authors', [])
        if authors:
            print(f"   Authors: ", end="")
            if len(authors) <= 3:
                print(", ".join(authors))
            else:
                print(f"{', '.join(authors[:3])} et al.")
        
        # Show journal and date
        print(f"   Journal: {article.get('journal', 'Unknown')}")
        print(f"   Published: {article.get('publication_date', 'Unknown')}")
        print(f"   URL: {article.get('abstract_url', '')}")

if __name__ == "__main__":
    asyncio.run(test_pubmed_search())