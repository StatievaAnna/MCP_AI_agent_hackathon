import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.medical_terminology_tool import MedicalTerminologyTool

async def test_icd_code_lookup():
    """Test the ICD-10 code lookup functionality"""
    print("\n=== Testing ICD-10 Code Lookup ===")
    
    # Initialize the tool
    tool = MedicalTerminologyTool()
    
    # Test searching by description
    print("\nSearching for 'diabetes' in ICD-10 codes...")
    result = await tool.lookup_icd_code(description="diabetes", max_results=5)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Search term: {result.get('search_term', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show codes
    codes = result.get('results', [])
    print(f"Returned {len(codes)} codes:")
    
    for i, code_info in enumerate(codes):
        print(f"\n{i+1}. {code_info.get('code', 'No code')}: {code_info.get('description', 'No description')}")
        print(f"   Category: {code_info.get('category', 'Unknown')}")
        
        # Show chapter information if available
        if 'chapter' in code_info and 'chapter_description' in code_info:
            print(f"   Chapter {code_info['chapter']}: {code_info['chapter_description']}")
    
    # Test searching by code
    print("\nSearching for ICD-10 code 'E11'...")
    result = await tool.lookup_icd_code(code="E11", max_results=5)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Search term: {result.get('search_term', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show codes
    codes = result.get('results', [])
    print(f"Returned {len(codes)} codes:")
    
    for i, code_info in enumerate(codes):
        print(f"\n{i+1}. {code_info.get('code', 'No code')}: {code_info.get('description', 'No description')}")
        print(f"   Category: {code_info.get('category', 'Unknown')}")
        
        # Show chapter information if available
        if 'chapter' in code_info and 'chapter_description' in code_info:
            print(f"   Chapter {code_info['chapter']}: {code_info['chapter_description']}")
    
    # Test error case (no parameters)
    print("\nTesting error case (no parameters)...")
    result = await tool.lookup_icd_code()
    print(f"Status: {result['status']}")
    print(f"Error message: {result.get('error_message', 'No error')}")

if __name__ == "__main__":
    asyncio.run(test_icd_code_lookup())