import asyncio
import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.clinical_trials_tool import ClinicalTrialsTool

@pytest.mark.asyncio
async def test_clinical_trials_search():
    """Test the clinical trials search functionality with real API"""
    print("\n=== Testing Clinical Trials Search ===")
    
    # Initialize the tool
    tool = ClinicalTrialsTool()
    
    # Test searching for diabetes trials from ClinicalTrials.gov
    print("\nSearching for diabetes trials (ClinicalTrials.gov)...")
    result = await tool.search_trials("diabetes", "recruiting", 3)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    
    # Print error message if there is one
    if result['status'] == 'error':
        print(f"Error: {result.get('error_message', 'Unknown error')}")
    
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show trials
    trials = result.get('trials', [])
    print(f"Returned {len(trials)} trials:")
    
    for i, trial in enumerate(trials):
        print(f"\n{i+1}. {trial.get('title', 'No title')}")
        print(f"   ID: {trial.get('nct_id', 'No ID')}")
        print(f"   Status: {trial.get('status', 'Unknown')}")
        print(f"   Phase: {trial.get('phase', 'Unknown')}")
        
        # Show locations (limited to first 2)
        locations = trial.get('locations', [])
        if locations:
            print(f"   Locations ({len(locations)} total):")
            for j, loc in enumerate(locations[:2]):
                print(f"     - {loc.get('facility', 'Unknown')} ({loc.get('city', '')}, {loc.get('state', '')})")
            if len(locations) > 2:
                print(f"     - ...and {len(locations) - 2} more")

@pytest.mark.asyncio
async def test_clinical_trials_search_with_mock():
    """Test the clinical trials search functionality with mock data"""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT12345678",
                        "briefTitle": "Test Diabetes Trial"
                    },
                    "statusModule": {
                        "overallStatus": "RECRUITING"
                    },
                    "designModule": {
                        "studyType": "INTERVENTIONAL",
                        "phases": ["PHASE_2", "PHASE_3"]
                    },
                    "conditionsModule": {
                        "conditions": ["Type 2 Diabetes", "Obesity"]
                    },
                    "contactsLocationsModule": {
                        "locations": [
                            {
                                "facility": {"name": "Test Hospital"},
                                "city": "Boston",
                                "state": "Massachusetts",
                                "country": "United States"
                            }
                        ]
                    },
                    "sponsorCollaboratorsModule": {
                        "leadSponsor": {"name": "Test Pharma Inc."}
                    },
                    "descriptionModule": {
                        "briefSummary": "A test trial for diabetes treatment"
                    },
                    "eligibilityModule": {
                        "sex": "ALL",
                        "minimumAge": "18 Years",
                        "maximumAge": "75 Years",
                        "healthyVolunteers": "No"
                    }
                }
            }
        ],
        "totalCount": 1
    }
    
    # Initialize the tool
    tool = ClinicalTrialsTool()
    
    # Mock the _make_request method instead of http_client.get
    with patch.object(tool, '_make_request', return_value=mock_response.json.return_value):
        # Test searching for diabetes trials
        result = await tool.search_trials("diabetes", "recruiting", 3)
        
        # Verify the result
        assert result['status'] == 'success'
        assert result['total_results'] == 1
        assert len(result['trials']) == 1
        
        trial = result['trials'][0]
        assert trial['nct_id'] == 'NCT12345678'
        assert trial['title'] == 'Test Diabetes Trial'
        assert trial['status'] == 'RECRUITING'
        assert trial['phase'] == 'PHASE_2, PHASE_3'
        assert trial['study_type'] == 'INTERVENTIONAL'
        assert trial['conditions'] == ['Type 2 Diabetes', 'Obesity']
        assert trial['sponsor'] == 'Test Pharma Inc.'
        assert trial['brief_summary'] == 'A test trial for diabetes treatment'
        assert len(trial['locations']) == 1
        assert trial['locations'][0]['facility'] == 'Test Hospital'
        assert trial['locations'][0]['city'] == 'Boston'
        assert trial['eligibility']['gender'] == 'ALL'
        assert trial['eligibility']['min_age'] == '18 Years'
        assert trial['eligibility']['max_age'] == '75 Years'

@pytest.mark.asyncio
async def test_clinical_trials_search_error_handling():
    """Test error handling in clinical trials search"""
    # Initialize the tool
    tool = ClinicalTrialsTool()
    
    # Test with empty condition
    result = await tool.search_trials("")
    assert result['status'] == 'error'
    assert 'Condition is required' in result['error_message']
    
    # Test with invalid max_results - mock the _make_request to avoid API errors
    with patch.object(tool, '_make_request', return_value={"studies": [], "totalCount": 0}):
        result = await tool.search_trials("diabetes", "recruiting", -5)
        assert result['status'] == 'success'  # Should correct the value, not error
    
    # Test with HTTP error - use a unique condition string to avoid cache hits
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("API Error")
    
    # Create a new tool instance with a unique condition string
    new_tool = ClinicalTrialsTool()
    
    # Mock the _make_request method to raise an exception
    with patch.object(new_tool, '_make_request', side_effect=Exception("API Error")):
        # Use a unique condition string to avoid cache hits
        result = await new_tool.search_trials("unique_test_condition_123")
        assert result['status'] == 'error'
        assert 'Error searching clinical trials' in result['error_message']

if __name__ == "__main__":
    asyncio.run(test_clinical_trials_search())