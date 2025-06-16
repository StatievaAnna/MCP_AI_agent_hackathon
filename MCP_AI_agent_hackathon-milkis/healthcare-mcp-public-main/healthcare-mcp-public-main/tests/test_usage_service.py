import pytest
import os
import time
import tempfile
import sqlite3
from datetime import datetime
from src.services.usage_service import UsageService

class TestUsageService:
    """Test suite for UsageService class"""
    
    @pytest.fixture
    def usage_service(self):
        """Create a UsageService instance with a temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
            service = UsageService(db_path=temp_db.name)
            yield service
    
    def test_init(self, usage_service):
        """Test UsageService initialization"""
        # Check if database was initialized
        conn = sqlite3.connect(usage_service.db_path)
        cursor = conn.cursor()
        
        # Check if usage table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage'")
        assert cursor.fetchone() is not None
        
        # Check if indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_session_timestamp'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_tool'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_record_usage(self, usage_service):
        """Test recording usage"""
        # Record some usage
        result = usage_service.record_usage("test_session", "test_tool", 1)
        assert result is True
        
        # Record more usage
        result = usage_service.record_usage("test_session", "another_tool", 2)
        assert result is True
        
        # Test with invalid inputs
        result = usage_service.record_usage("", "test_tool", 1)
        assert result is False
        
        result = usage_service.record_usage("test_session", "", 1)
        assert result is False
    
    def test_get_monthly_usage(self, usage_service):
        """Test getting monthly usage"""
        # Record some usage
        usage_service.record_usage("test_session", "tool1", 1)
        usage_service.record_usage("test_session", "tool2", 2)
        usage_service.record_usage("test_session", "tool1", 3)
        usage_service.record_usage("different_session", "tool1", 5)
        
        # Get monthly usage for the test session
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year
        
        usage = usage_service.get_monthly_usage("test_session", month, year)
        
        # Check structure
        assert usage["session_id"] == "test_session"
        assert usage["month"] == month
        assert usage["year"] == year
        assert usage["total_api_calls"] == 6  # 1 + 2 + 3
        assert "tool_usage" in usage
        assert "daily_usage" in usage
        
        # Check tool usage
        assert usage["tool_usage"]["tool1"] == 4  # 1 + 3
        assert usage["tool_usage"]["tool2"] == 2
        
        # Check daily usage
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in usage["daily_usage"]
        assert usage["daily_usage"][today] == 6
        
        # Test with non-existent session
        usage = usage_service.get_monthly_usage("nonexistent_session", month, year)
        assert usage["total_api_calls"] == 0
        assert usage["tool_usage"] == {}
        assert usage["daily_usage"] == {}
    
    def test_get_usage_stats(self, usage_service):
        """Test getting overall usage statistics"""
        # Record some usage
        usage_service.record_usage("session1", "tool1", 1)
        usage_service.record_usage("session1", "tool2", 2)
        usage_service.record_usage("session2", "tool1", 3)
        usage_service.record_usage("session3", "tool3", 4)
        
        # Get overall stats
        stats = usage_service.get_usage_stats()
        
        # Check structure
        assert "total_api_calls" in stats
        assert "total_unique_sessions" in stats
        assert "tool_usage" in stats
        assert "monthly_usage" in stats
        
        # Check values
        assert stats["total_api_calls"] == 10  # 1 + 2 + 3 + 4
        assert stats["total_unique_sessions"] == 3
        
        # Check tool usage
        assert stats["tool_usage"]["tool1"] == 4  # 1 + 3
        assert stats["tool_usage"]["tool2"] == 2
        assert stats["tool_usage"]["tool3"] == 4
        
        # Check monthly usage
        current_month = datetime.now().strftime("%Y-%m")
        assert current_month in stats["monthly_usage"]
        assert stats["monthly_usage"][current_month] == 10
    
    def test_cleanup_old_data(self, usage_service):
        """Test cleaning up old data"""
        # Record some usage
        usage_service.record_usage("session1", "tool1", 1)
        
        # Manually insert old data
        conn = usage_service._get_connection()
        cursor = conn.cursor()
        
        # Insert data from 400 days ago
        old_timestamp = time.time() - (400 * 86400)
        cursor.execute(
            "INSERT INTO usage (session_id, tool, timestamp, api_calls) VALUES (?, ?, ?, ?)",
            ("old_session", "old_tool", old_timestamp, 5)
        )
        conn.commit()
        
        # Clean up data older than 365 days
        deleted = usage_service.cleanup_old_data(365)
        assert deleted == 1
        
        # Verify old data is gone
        cursor.execute("SELECT COUNT(*) FROM usage WHERE session_id = 'old_session'")
        count = cursor.fetchone()[0]
        assert count == 0
        
        # Verify recent data is still there
        cursor.execute("SELECT COUNT(*) FROM usage WHERE session_id = 'session1'")
        count = cursor.fetchone()[0]
        assert count == 1