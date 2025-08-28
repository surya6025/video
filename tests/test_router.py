"""
Tests for the intent router and skill routing system
"""

import pytest
from unittest.mock import Mock, patch
from core.router import IntentClassifier, SkillRouter

class TestIntentClassifier:
    """Test the IntentClassifier class"""
    
    def test_init(self):
        """Test classifier initialization"""
        classifier = IntentClassifier()
        assert classifier is not None
        assert hasattr(classifier, 'patterns')
        assert hasattr(classifier, 'model')
    
    def test_rule_based_classification(self):
        """Test rule-based intent classification"""
        classifier = IntentClassifier()
        
        # Test NLP patterns
        result = classifier.classify("Summarize this text")
        assert result['intent'] == 'nlp'
        assert result['confidence'] > 0.8
        
        # Test ML patterns
        result = classifier.classify("Train a machine learning model")
        assert result['intent'] == 'ml'
        assert result['confidence'] > 0.8
        
        # Test data science patterns
        result = classifier.classify("Analyze this dataset")
        assert result['intent'] == 'data_science'
        assert result['confidence'] > 0.8
    
    def test_ml_classification(self):
        """Test ML-based intent classification"""
        classifier = IntentClassifier()
        
        # Test with synthetic data
        result = classifier.classify("Create a visualization")
        assert result['intent'] in ['data_science', 'analytics']
        assert result['confidence'] > 0.5
    
    def test_confidence_scoring(self):
        """Test confidence scoring mechanism"""
        classifier = IntentClassifier()
        
        result = classifier.classify("This is a very specific NLP task")
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1
    
    def test_fallback_classification(self):
        """Test fallback to general intent"""
        classifier = IntentClassifier()
        
        result = classifier.classify("Random text that doesn't match patterns")
        assert result['intent'] == 'general'
        assert result['confidence'] < 0.5

class TestSkillRouter:
    """Test the SkillRouter class"""
    
    def test_init(self):
        """Test router initialization"""
        router = SkillRouter()
        assert router is not None
        assert hasattr(router, 'skill_mapping')
    
    def test_route_to_skill(self):
        """Test routing to specific skills"""
        router = SkillRouter()
        
        # Test NLP routing
        skill_path = router.route_intent('nlp')
        assert skill_path == 'skills.nlp.NLPSkill'
        
        # Test ML routing
        skill_path = router.route_intent('ml')
        assert skill_path == 'skills.ml.MLSkill'
        
        # Test data science routing
        skill_path = router.route_intent('data_science')
        assert skill_path == 'skills.data_science.DataScienceSkill'
    
    def test_unknown_intent(self):
        """Test handling of unknown intents"""
        router = SkillRouter()
        
        skill_path = router.route_intent('unknown_intent')
        assert skill_path == 'skills.nlp.NLPSkill'  # Default fallback
    
    def test_skill_mapping_completeness(self):
        """Test that all intents have skill mappings"""
        router = SkillRouter()
        
        expected_intents = [
            'nlp', 'ml', 'data_science', 'data_engineering',
            'analytics', 'automation', 'cybersecurity', 'system_control',
            'ui_ux', 'web_search'
        ]
        
        for intent in expected_intents:
            skill_path = router.route_intent(intent)
            assert skill_path is not None
            assert '.' in skill_path  # Should be a module path

class TestRouterIntegration:
    """Test router integration with classifier"""
    
    def test_end_to_end_routing(self):
        """Test complete routing flow"""
        classifier = IntentClassifier()
        router = SkillRouter()
        
        # Test complete flow
        query = "Train a machine learning model on this data"
        classification = classifier.classify(query)
        skill_path = router.route_intent(classification['intent'])
        
        assert classification['intent'] == 'ml'
        assert skill_path == 'skills.ml.MLSkill'
    
    def test_confidence_thresholds(self):
        """Test routing with different confidence levels"""
        classifier = IntentClassifier()
        router = SkillRouter()
        
        # High confidence query
        high_conf_query = "Summarize this document"
        high_conf_result = classifier.classify(high_conf_query)
        
        # Low confidence query
        low_conf_query = "Random gibberish text"
        low_conf_result = classifier.classify(low_conf_query)
        
        assert high_conf_result['confidence'] > low_conf_result['confidence']
        
        # Both should still route to skills
        high_conf_skill = router.route_intent(high_conf_result['intent'])
        low_conf_skill = router.route_intent(low_conf_result['intent'])
        
        assert high_conf_skill is not None
        assert low_conf_skill is not None