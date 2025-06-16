import pytest
import os
import time
import tempfile
import sqlite3
from src.services.cache_service import CacheService

class TestCacheService:
    """Test suite for CacheService class"""
    
    @pytest.fixture
    def cache_service(self):
        """Create a CacheService instance with a temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
            service = CacheService(db_path=temp_db.name, ttl=10)  # Short TTL for testing
            yield service
    
    def test_init(self, cache_service):
        """Test CacheService initialization"""
        assert cache_service.default_ttl == 10
        
        # Check if database was initialized
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        
        # Check if cache table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
        assert cursor.fetchone() is not None
        
        # Check if index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_expires_at'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_set_get(self, cache_service):
        """Test setting and getting cache values"""
        # Set a value
        test_key = "test_key"
        test_value = {"data": "test_value", "nested": {"key": "value"}}
        
        result = cache_service.set(test_key, test_value)
        assert result is True
        
        # Get the value
        retrieved = cache_service.get(test_key)
        assert retrieved == test_value
        
        # Test with different types
        types_to_test = [
            "string value",
            123,
            12.34,
            True,
            [1, 2, 3],
            {"a": 1, "b": 2},
            None
        ]
        
        for i, value in enumerate(types_to_test):
            key = f"test_key_{i}"
            cache_service.set(key, value)
            assert cache_service.get(key) == value
    
    def test_expiration(self, cache_service):
        """Test cache expiration"""
        # Set a value with a very short TTL
        test_key = "expiring_key"
        test_value = "This will expire soon"
        
        cache_service.set(test_key, test_value, ttl=1)  # 1 second TTL
        
        # Verify it exists initially
        assert cache_service.get(test_key) == test_value
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Verify it's gone
        assert cache_service.get(test_key) is None
    
    def test_delete(self, cache_service):
        """Test deleting cache entries"""
        # Set a value
        test_key = "delete_me"
        test_value = "This will be deleted"
        
        cache_service.set(test_key, test_value)
        assert cache_service.get(test_key) == test_value
        
        # Delete it
        result = cache_service.delete(test_key)
        assert result is True
        
        # Verify it's gone
        assert cache_service.get(test_key) is None
        
        # Try to delete non-existent key
        result = cache_service.delete("nonexistent_key")
        assert result is False
    
    def test_clear_expired(self, cache_service):
        """Test clearing expired entries"""
        # Set some values with different TTLs
        cache_service.set("expire_1", "Value 1", ttl=1)
        cache_service.set("expire_2", "Value 2", ttl=1)
        cache_service.set("keep_1", "Keep this", ttl=30)
        
        # Wait for some to expire
        time.sleep(1.5)
        
        # Clear expired entries
        deleted = cache_service.clear_expired()
        assert deleted == 2  # Should have deleted 2 entries
        
        # Verify expired entries are gone
        assert cache_service.get("expire_1") is None
        assert cache_service.get("expire_2") is None
        
        # Verify non-expired entry is still there
        assert cache_service.get("keep_1") == "Keep this"
    
    def test_get_stats(self, cache_service):
        """Test getting cache statistics"""
        # Set some values
        cache_service.set("stats_1", "Value 1", ttl=1)
        cache_service.set("stats_2", "Value 2", ttl=30)
        cache_service.set("stats_3", "Value 3", ttl=30)
        
        # Wait for one to expire
        time.sleep(1.5)
        
        # Get stats
        stats = cache_service.get_stats()
        
        # Check stats structure
        assert "total_entries" in stats
        assert "expired_entries" in stats
        assert "valid_entries" in stats
        assert "average_ttl_seconds" in stats
        
        # Verify counts
        assert stats["total_entries"] == 3
        assert stats["expired_entries"] == 1
        assert stats["valid_entries"] == 2
        assert stats["average_ttl_seconds"] > 0