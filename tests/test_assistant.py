"""
Tests for the main assistant orchestrator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.assistant import JarvisXAssistant

class TestJarvisXAssistant:
    """Test the JarvisXAssistant class"""
    
    def test_init(self, mock_llm, mock_memory, mock_permissions):
        """Test assistant initialization"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        assert assistant.llm == mock_llm
        assert assistant.memory == mock_memory
        assert assistant.permissions == mock_permissions
        assert hasattr(assistant, 'session')
        assert hasattr(assistant, 'skill_cache')
    
    def test_initialize_session(self, mock_llm, mock_memory, mock_permissions):
        """Test session initialization"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        session = assistant.initialize_session("test_user")
        
        assert session['user_id'] == "test_user"
        assert 'session_id' in session
        assert 'conversation_id' in session
        assert 'timestamp' in session
    
    def test_process_message_basic(self, mock_llm, mock_memory, mock_permissions):
        """Test basic message processing"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock the router
        with patch('core.assistant.IntentClassifier') as mock_classifier, \
             patch('core.assistant.SkillRouter') as mock_router:
            
            mock_classifier.return_value.classify.return_value = {
                'intent': 'nlp',
                'confidence': 0.9
            }
            mock_router.return_value.route_intent.return_value = 'skills.nlp.NLPSkill'
            
            # Mock skill loading
            with patch('core.assistant.importlib.import_module') as mock_import:
                mock_module = Mock()
                mock_skill_class = Mock()
                mock_skill_instance = Mock()
                mock_skill_instance.run.return_value = {
                    'type': 'text',
                    'content': 'Test response',
                    'artifacts': [],
                    'metadata': {'operation': 'test'}
                }
                mock_skill_class.return_value = mock_skill_instance
                mock_module.NLPSkill = mock_skill_class
                mock_import.return_value = mock_module
                
                result = assistant.process_message("Hello", "test_user")
                
                assert result['type'] == 'text'
                assert 'Test response' in result['content']
    
    def test_process_message_with_clarification(self, mock_llm, mock_memory, mock_permissions):
        """Test message processing with clarification needed"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock low confidence classification
        with patch('core.assistant.IntentClassifier') as mock_classifier:
            mock_classifier.return_value.classify.return_value = {
                'intent': 'general',
                'confidence': 0.3
            }
            
            result = assistant.process_message("Unclear query", "test_user")
            
            assert result['type'] == 'clarification'
            assert 'clarification' in result['content'].lower()
    
    def test_process_message_with_fallback(self, mock_llm, mock_memory, mock_permissions):
        """Test message processing with fallback to general skill"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock skill loading failure
        with patch('core.assistant.IntentClassifier') as mock_classifier, \
             patch('core.assistant.SkillRouter') as mock_router, \
             patch('core.assistant.importlib.import_module') as mock_import:
            
            mock_classifier.return_value.classify.return_value = {
                'intent': 'ml',
                'confidence': 0.8
            }
            mock_router.return_value.route_intent.return_value = 'skills.ml.MLSkill'
            mock_import.side_effect = ImportError("Skill not found")
            
            result = assistant.process_message("Train a model", "test_user")
            
            assert result['type'] == 'text'
            assert 'fallback' in result['content'].lower()
    
    def test_skill_caching(self, mock_llm, mock_memory, mock_permissions):
        """Test that skills are cached after first load"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock skill loading
        with patch('core.assistant.IntentClassifier') as mock_classifier, \
             patch('core.assistant.SkillRouter') as mock_router, \
             patch('core.assistant.importlib.import_module') as mock_import:
            
            mock_classifier.return_value.classify.return_value = {
                'intent': 'nlp',
                'confidence': 0.9
            }
            mock_router.return_value.route_intent.return_value = 'skills.nlp.NLPSkill'
            
            mock_module = Mock()
            mock_skill_class = Mock()
            mock_skill_instance = Mock()
            mock_skill_instance.run.return_value = {
                'type': 'text',
                'content': 'Test response',
                'artifacts': [],
                'metadata': {'operation': 'test'}
            }
            mock_skill_class.return_value = mock_skill_instance
            mock_module.NLPSkill = mock_skill_class
            mock_import.return_value = mock_module
            
            # First call should load skill
            result1 = assistant.process_message("Hello", "test_user")
            
            # Second call should use cached skill
            result2 = assistant.process_message("Hello again", "test_user")
            
            # Import should only be called once
            assert mock_import.call_count == 1
            
            # Both calls should succeed
            assert result1['type'] == 'text'
            assert result2['type'] == 'text'
    
    def test_conversation_persistence(self, mock_llm, mock_memory, mock_permissions):
        """Test that conversations are persisted to memory"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock successful message processing
        with patch('core.assistant.IntentClassifier') as mock_classifier, \
             patch('core.assistant.SkillRouter') as mock_router, \
             patch('core.assistant.importlib.import_module') as mock_import:
            
            mock_classifier.return_value.classify.return_value = {
                'intent': 'nlp',
                'confidence': 0.9
            }
            mock_router.return_value.route_intent.return_value = 'skills.nlp.NLPSkill'
            
            mock_module = Mock()
            mock_skill_class = Mock()
            mock_skill_instance = Mock()
            mock_skill_instance.run.return_value = {
                'type': 'text',
                'content': 'Test response',
                'artifacts': [],
                'metadata': {'operation': 'test'}
            }
            mock_skill_class.return_value = mock_skill_instance
            mock_module.NLPSkill = mock_skill_class
            mock_import.return_value = mock_module
            
            # Process message
            assistant.process_message("Hello", "test_user")
            
            # Verify memory calls were made
            mock_memory.save_conversation.assert_called()
            mock_memory.save_message.assert_called()
    
    def test_error_handling(self, mock_llm, mock_memory, mock_permissions):
        """Test error handling in message processing"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock an error during processing
        with patch('core.assistant.IntentClassifier') as mock_classifier:
            mock_classifier.return_value.classify.side_effect = Exception("Test error")
            
            result = assistant.process_message("Hello", "test_user")
            
            assert result['type'] == 'error'
            assert 'error' in result['content'].lower()
    
    def test_permission_checking(self, mock_llm, mock_memory, mock_permissions):
        """Test that permissions are checked before skill execution"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Mock permission check
        mock_permissions.check_permission.return_value = False
        
        # Mock skill that requires permission
        with patch('core.assistant.IntentClassifier') as mock_classifier, \
             patch('core.assistant.SkillRouter') as mock_router, \
             patch('core.assistant.importlib.import_module') as mock_import:
            
            mock_classifier.return_value.classify.return_value = {
                'intent': 'ml',
                'confidence': 0.9
            }
            mock_router.return_value.route_intent.return_value = 'skills.ml.MLSkill'
            
            mock_module = Mock()
            mock_skill_class = Mock()
            mock_skill_instance = Mock()
            mock_skill_instance.requires_permission = "MODEL_TRAINING"
            mock_skill_class.return_value = mock_skill_instance
            mock_module.MLSkill = mock_skill_class
            mock_import.return_value = mock_module
            
            result = assistant.process_message("Train a model", "test_user")
            
            assert result['type'] == 'error'
            assert 'permission' in result['content'].lower()
            
            # Permission should have been checked
            mock_permissions.check_permission.assert_called()
    
    def test_session_management(self, mock_llm, mock_memory, mock_permissions):
        """Test session management functionality"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        # Test session creation
        session1 = assistant.initialize_session("user1")
        session2 = assistant.initialize_session("user2")
        
        assert session1['user_id'] == "user1"
        assert session2['user_id'] == "user2"
        assert session1['session_id'] != session2['session_id']
        
        # Test session retrieval
        retrieved_session = assistant.get_session("user1")
        assert retrieved_session['user_id'] == "user1"
    
    def test_skill_info_retrieval(self, mock_llm, mock_memory, mock_permissions):
        """Test retrieving information about available skills"""
        assistant = JarvisXAssistant(
            llm=mock_llm,
            memory=mock_memory,
            permissions=mock_permissions
        )
        
        skills_info = assistant.get_available_skills()
        
        assert isinstance(skills_info, list)
        assert len(skills_info) > 0
        
        for skill_info in skills_info:
            assert 'name' in skill_info
            assert 'description' in skill_info
            assert 'capabilities' in skill_info