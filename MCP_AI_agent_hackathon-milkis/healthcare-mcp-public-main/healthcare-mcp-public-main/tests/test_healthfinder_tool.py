import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.healthfinder_tool import HealthFinderTool

async def test_health_topics():
    """Test the Health Topics functionality"""
    print("\n=== Testing Health Topics ===")
    
    # Initialize the tool
    tool = HealthFinderTool()
    
    # Test searching for a health topic in English
    print("\nSearching for 'nutrition' in English...")
    result = await tool.get_health_topics("nutrition", "en")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Search term: {result.get('search_term', '')}")
    print(f"Language: {result.get('language', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show topics
    topics = result.get('topics', [])
    print(f"Returned {len(topics)} topics:")
    
    for i, topic in enumerate(topics):
        if i >= 3:  # Limit to first 3 results for readability
            print(f"\n...and {len(topics) - 3} more topics")
            break
            
        print(f"\n{i+1}. {topic.get('title', 'No title')}")
        print(f"   URL: {topic.get('url', '')}")
        print(f"   Last updated: {topic.get('last_updated', 'Unknown')}")
        print(f"   Section: {topic.get('section', 'Unknown')}")
        
        if 'description' in topic and topic['description']:
            description = topic['description']
            if len(description) > 150:
                description = description[:147] + "..."
            print(f"   Description: {description}")
    
    # Test searching for a health topic in Spanish
    print("\nSearching for 'diabetes' in Spanish...")
    result = await tool.get_health_topics("diabetes", "es")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Search term: {result.get('search_term', '')}")
    print(f"Language: {result.get('language', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show topics
    topics = result.get('topics', [])
    print(f"Returned {len(topics)} topics:")
    
    for i, topic in enumerate(topics):
        if i >= 3:  # Limit to first 3 results for readability
            print(f"\n...and {len(topics) - 3} more topics")
            break
            
        print(f"\n{i+1}. {topic.get('title', 'No title')}")
        print(f"   URL: {topic.get('url', '')}")
        print(f"   Last updated: {topic.get('last_updated', 'Unknown')}")
        print(f"   Section: {topic.get('section', 'Unknown')}")
        
        if 'description' in topic and topic['description']:
            description = topic['description']
            if len(description) > 150:
                description = description[:147] + "..."
            print(f"   Description: {description}")
    
    # Test searching for a very specific health topic
    print("\nSearching for 'immunization schedule'...")
    result = await tool.get_health_topics("immunization schedule")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Search term: {result.get('search_term', '')}")
    print(f"Language: {result.get('language', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show topics
    topics = result.get('topics', [])
    print(f"Returned {len(topics)} topics:")
    
    for i, topic in enumerate(topics):
        if i >= 3:  # Limit to first 3 results for readability
            print(f"\n...and {len(topics) - 3} more topics")
            break
            
        print(f"\n{i+1}. {topic.get('title', 'No title')}")
        print(f"   URL: {topic.get('url', '')}")
        print(f"   Last updated: {topic.get('last_updated', 'Unknown')}")
        print(f"   Section: {topic.get('section', 'Unknown')}")
        
        if 'description' in topic and topic['description']:
            description = topic['description']
            if len(description) > 150:
                description = description[:147] + "..."
            print(f"   Description: {description}")

if __name__ == "__main__":
    asyncio.run(test_health_topics())