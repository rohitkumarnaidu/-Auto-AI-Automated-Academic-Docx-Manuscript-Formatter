"""
Database Layer Tests
Tests database connection and Supabase client properly initializes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

class TestDatabaseLayer:
    """Test suite for database layer."""
    
    @pytest.mark.database
    def test_supabase_client_creation(self):
        """Test Supabase client can be created."""
        with patch('app.db.supabase_client.create_client') as mock_create_client:
            with patch('app.db.supabase_client.settings') as mock_settings:
                mock_settings.SUPABASE_URL = "http://localhost:8000"
                mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test_key"
                
                from app.db.supabase_client import get_supabase_client
                
                client = get_supabase_client()
                assert mock_create_client.called
    
    @pytest.mark.database
    def test_graceful_degradation_on_connection_failure(self):
        """Test graceful degradation when database unavailable."""
        with patch('app.db.supabase_client.create_client') as mock_create_client:
            mock_create_client.side_effect = Exception("Connection failed")
            
            from app.db.supabase_client import get_supabase_client
            
            # Should handle exception and return None
            client = get_supabase_client()
            assert client is None
    
    @pytest.mark.database
    def test_missing_credentials(self):
        """Test client creation fails gracefully with missing credentials."""
        with patch('app.db.supabase_client.settings') as mock_settings:
            mock_settings.SUPABASE_URL = ""
            mock_settings.SUPABASE_SERVICE_ROLE_KEY = ""
            
            from app.db.supabase_client import get_supabase_client
            
            # Should handle missing creds and return None
            client = get_supabase_client()
            assert client is None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "database"])
