import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.tools.base_tool import BaseTool

class TestBaseTool:
    """Test suite for BaseTool class"""
    
    @pytest.fixture
    def base_tool(self):
        """Create a BaseTool instance with a temporary cache database"""
        with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
            tool = BaseTool(cache_db_path=temp_db.name)
            yield tool
    
    def test_init(self, base_tool):
        """Test BaseTool initialization"""
        assert base_tool.cache is not None
        assert base_tool.api_key is None
        assert base_tool.base_url is None
    
    def test_get_cache_key(self, base_tool):
        """Test cache key generation"""
        # Test with simple arguments
        key1 = base_tool._get_cache_key("test", "arg1", "arg2")
        assert isinstance(key1, str)
        assert len(key1) > 0
        
        # Test with None arguments
        key2 = base_tool._get_cache_key("test", "arg1", None, "arg3")
        assert isinstance(key2, str)
        assert len(key2) > 0
        
        # Test with different arguments should produce different keys
        key3 = base_tool._get_cache_key("test", "arg1", "different")
        assert key1 != key3
    
    @patch('requests.request')
    async def test_make_request(self, mock_request, base_tool):
        """Test HTTP request functionality"""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_request.return_value = mock_response
        
        # Test GET request
        result = await base_tool._make_request("https://example.com/api")
        assert result == {"status": "success", "data": "test"}
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://example.com/api"
        assert kwargs["params"] is None
        assert kwargs["data"] is None
        assert kwargs["json"] is None
        assert kwargs["timeout"] == 30
        
        # Reset mock
        mock_request.reset_mock()
        
        # Test POST request with parameters
        params = {"param1": "value1"}
        headers = {"Content-Type": "application/json"}
        json_data = {"key": "value"}
        
        result = await base_tool._make_request(
            "https://example.com/api",
            method="POST",
            params=params,
            headers=headers,
            json_data=json_data
        )
        
        assert result == {"status": "success", "data": "test"}
        mock_request.assert_called_once_with(
            method="POST",
            url="https://example.com/api",
            params=params,
            headers=headers,
            data=None,
            json=json_data,
            timeout=30
        )
    
    def test_format_error_response(self, base_tool):
        """Test error response formatting"""
        error_msg = "Test error message"
        response = base_tool._format_error_response(error_msg)
        
        assert response["status"] == "error"
        assert response["error_message"] == error_msg
    
    def test_format_success_response(self, base_tool):
        """Test success response formatting"""
        # Test with no additional data
        response1 = base_tool._format_success_response()
        assert response1["status"] == "success"
        
        # Test with additional data
        response2 = base_tool._format_success_response(
            data="test_data",
            count=5,
            items=["item1", "item2"]
        )
        assert response2["status"] == "success"
        assert response2["data"] == "test_data"
        assert response2["count"] == 5
        assert response2["items"] == ["item1", "item2"]