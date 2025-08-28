"""
Tests for the memory system
"""

import pytest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch
from core.memory import LocalCache, SupabaseMemory

class TestLocalCache:
    """Test the LocalCache class"""
    
    def test_init(self, temp_dir):
        """Test cache initialization"""
        cache = LocalCache(temp_dir)
        assert cache.db_path == os.path.join(temp_dir, 'jarvisx_cache.db')
        assert os.path.exists(cache.db_path)
    
    def test_create_tables(self, temp_dir):
        """Test table creation"""
        cache = LocalCache(temp_dir)
        
        # Check if tables exist
        conn = sqlite3.connect(cache.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['profiles', 'conversations', 'messages', 'permissions']
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    def test_profile_operations(self, temp_dir):
        """Test profile CRUD operations"""
        cache = LocalCache(temp_dir)
        
        # Create profile
        profile_data = {"name": "Test User", "email": "test@example.com"}
        profile_id = cache.save_profile(profile_data)
        assert profile_id is not None
        
        # Retrieve profile
        retrieved = cache.get_profile(profile_id)
        assert retrieved['name'] == "Test User"
        assert retrieved['email'] == "test@example.com"
        
        # Update profile
        updated_data = {"name": "Updated User", "email": "updated@example.com"}
        cache.update_profile(profile_id, updated_data)
        
        retrieved = cache.get_profile(profile_id)
        assert retrieved['name'] == "Updated User"
    
    def test_conversation_operations(self, temp_dir):
        """Test conversation CRUD operations"""
        cache = LocalCache(temp_dir)
        
        # Create conversation
        conv_data = {"title": "Test Conversation", "user_id": "user123"}
        conv_id = cache.save_conversation(conv_data)
        assert conv_id is not None
        
        # Retrieve conversation
        retrieved = cache.get_conversation(conv_id)
        assert retrieved['title'] == "Test Conversation"
        
        # List conversations
        conversations = cache.list_conversations("user123")
        assert len(conversations) == 1
        assert conversations[0]['title'] == "Test Conversation"
    
    def test_message_operations(self, temp_dir):
        """Test message CRUD operations"""
        cache = LocalCache(temp_dir)
        
        # Create message
        msg_data = {
            "conversation_id": "conv123",
            "content": "Hello, world!",
            "role": "user",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        msg_id = cache.save_message(msg_data)
        assert msg_id is not None
        
        # Retrieve message
        retrieved = cache.get_message(msg_id)
        assert retrieved['content'] == "Hello, world!"
        assert retrieved['role'] == "user"
        
        # List messages
        messages = cache.list_messages("conv123")
        assert len(messages) == 1
        assert messages[0]['content'] == "Hello, world!"
    
    def test_permission_operations(self, temp_dir):
        """Test permission CRUD operations"""
        cache = LocalCache(temp_dir)
        
        # Create permission
        perm_data = {
            "user_id": "user123",
            "capability": "FILE_WRITE",
            "policy": "ask-every-time"
        }
        perm_id = cache.save_permission(perm_data)
        assert perm_id is not None
        
        # Retrieve permission
        retrieved = cache.get_permission(perm_id)
        assert retrieved['capability'] == "FILE_WRITE"
        assert retrieved['policy'] == "ask-every-time"
        
        # Update permission
        cache.update_permission(perm_id, {"policy": "always-allow"})
        retrieved = cache.get_permission(perm_id)
        assert retrieved['policy'] == "always-allow"

class TestSupabaseMemory:
    """Test the SupabaseMemory class"""
    
    @patch('core.memory.create_client')
    def test_init(self, mock_create_client):
        """Test Supabase initialization"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        memory = SupabaseMemory("test_url", "test_key")
        assert memory.client == mock_client
    
    @patch('core.memory.create_client')
    def test_profile_operations(self, mock_create_client):
        """Test Supabase profile operations"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock responses
        mock_client.table().insert().execute.return_value.data = [{"id": "prof123"}]
        mock_client.table().select().eq().execute.return_value.data = [{"id": "prof123", "name": "Test"}]
        
        memory = SupabaseMemory("test_url", "test_key")
        
        # Test save profile
        profile_id = memory.save_profile({"name": "Test"})
        assert profile_id == "prof123"
        
        # Test get profile
        profile = memory.get_profile("prof123")
        assert profile['name'] == "Test"
    
    @patch('core.memory.create_client')
    def test_conversation_operations(self, mock_create_client):
        """Test Supabase conversation operations"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock responses
        mock_client.table().insert().execute.return_value.data = [{"id": "conv123"}]
        mock_client.table().select().eq().execute.return_value.data = [{"id": "conv123", "title": "Test"}]
        
        memory = SupabaseMemory("test_url", "test_key")
        
        # Test save conversation
        conv_id = memory.save_conversation({"title": "Test"})
        assert conv_id == "conv123"
        
        # Test get conversation
        conv = memory.get_conversation("conv123")
        assert conv['title'] == "Test"
    
    @patch('core.memory.create_client')
    def test_error_handling(self, mock_create_client):
        """Test error handling in Supabase operations"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock error response
        mock_client.table().insert().execute.side_effect = Exception("Connection error")
        
        memory = SupabaseMemory("test_url", "test_key")
        
        # Test error handling
        with pytest.raises(Exception):
            memory.save_profile({"name": "Test"})

class TestMemoryIntegration:
    """Test memory system integration"""
    
    def test_fallback_mechanism(self, temp_dir):
        """Test fallback from Supabase to local cache"""
        # This would test the actual fallback mechanism
        # when Supabase is unavailable
        pass
    
    def test_data_consistency(self, temp_dir):
        """Test data consistency between local and remote"""
        # This would test that data stays consistent
        # between local cache and Supabase
        pass