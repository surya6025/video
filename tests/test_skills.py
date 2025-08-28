"""
Tests for all skills
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from skills.base_skill import BaseSkill
from skills.nlp import NLPSkill
from skills.ml import MLSkill
from skills.data_science import DataScienceSkill

class TestBaseSkill:
    """Test the BaseSkill abstract class"""
    
    def test_base_skill_abstract(self):
        """Test that BaseSkill cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseSkill()
    
    def test_base_skill_methods(self):
        """Test that BaseSkill has all required methods"""
        # Check that all required methods exist
        required_methods = [
            'run', 'get_info', 'validate_input', 'preprocess_query',
            'postprocess_result', 'handle_error', 'get_usage_examples',
            'get_help_text'
        ]
        
        for method in required_methods:
            assert hasattr(BaseSkill, method)

class TestNLPSkill:
    """Test the NLPSkill class"""
    
    def test_init(self):
        """Test NLP skill initialization"""
        skill = NLPSkill()
        assert skill.name == "Natural Language Processing"
        assert "summarization" in skill.capabilities
        assert "translation" in skill.capabilities
    
    def test_get_info(self):
        """Test getting skill information"""
        skill = NLPSkill()
        info = skill.get_info()
        
        assert info['name'] == "Natural Language Processing"
        assert info['description'] is not None
        assert len(info['capabilities']) > 0
    
    def test_validate_input(self):
        """Test input validation"""
        skill = NLPSkill()
        
        # Valid input
        assert skill.validate_input("Summarize this text") is True
        
        # Invalid input (empty)
        assert skill.validate_input("") is False
        
        # Invalid input (too short)
        assert skill.validate_input("Hi") is False
    
    def test_preprocess_query(self):
        """Test query preprocessing"""
        skill = NLPSkill()
        
        query = "  Summarize this text  "
        processed = skill.preprocess_query(query)
        
        assert processed == "Summarize this text"
        assert len(processed) < len(query)  # Should trim whitespace
    
    def test_get_usage_examples(self):
        """Test usage examples"""
        skill = NLPSkill()
        examples = skill.get_usage_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        for example in examples:
            assert 'query' in example
            assert 'description' in example
    
    def test_get_help_text(self):
        """Test help text"""
        skill = NLPSkill()
        help_text = skill.get_help_text()
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "Natural Language Processing" in help_text
    
    @patch('skills.nlp.LLMManager')
    def test_run_summarization(self, mock_llm_manager):
        """Test summarization operation"""
        skill = NLPSkill()
        
        # Mock LLM response
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is a summary of the text."
        mock_llm_manager.return_value.get_llm.return_value = mock_llm
        
        result = skill.run("Summarize this long text", {})
        
        assert result['type'] == 'text'
        assert 'summary' in result['content'].lower()
        assert result['metadata']['operation'] == 'summarization'
    
    @patch('skills.nlp.LLMManager')
    def test_run_translation(self, mock_llm_manager):
        """Test translation operation"""
        skill = NLPSkill()
        
        # Mock LLM response
        mock_llm = Mock()
        mock_llm.generate.return_value = "Bonjour le monde"
        mock_llm_manager.return_value.get_llm.return_value = mock_llm
        
        result = skill.run("Translate 'Hello world' to French", {})
        
        assert result['type'] == 'text'
        assert result['metadata']['operation'] == 'translation'
    
    def test_handle_error(self):
        """Test error handling"""
        skill = NLPSkill()
        
        error = Exception("Test error")
        result = skill.handle_error(error, "test query")
        
        assert result['type'] == 'error'
        assert 'error' in result['content'].lower()
        assert result['metadata']['error_type'] == 'Exception'

class TestMLSkill:
    """Test the MLSkill class"""
    
    def test_init(self):
        """Test ML skill initialization"""
        skill = MLSkill()
        assert skill.name == "Machine Learning"
        assert "model_training" in skill.capabilities
        assert "prediction" in skill.capabilities
        assert skill.requires_permission == "MODEL_TRAINING"
    
    def test_get_info(self):
        """Test getting skill information"""
        skill = MLSkill()
        info = skill.get_info()
        
        assert info['name'] == "Machine Learning"
        assert info['description'] is not None
        assert len(info['capabilities']) > 0
    
    def test_validate_input(self):
        """Test input validation"""
        skill = MLSkill()
        
        # Valid input
        assert skill.validate_input("Train a model on this data") is True
        
        # Invalid input (empty)
        assert skill.validate_input("") is False
    
    @patch('skills.ml.pd.read_csv')
    @patch('skills.ml.sklearn.linear_model.LogisticRegression')
    def test_run_model_training(self, mock_lr, mock_read_csv):
        """Test model training operation"""
        skill = MLSkill()
        
        # Mock pandas and sklearn
        mock_data = Mock()
        mock_data.shape = (100, 5)
        mock_data.columns = ['feature1', 'feature2', 'feature3', 'feature4', 'target']
        mock_read_csv.return_value = mock_data
        
        mock_model = Mock()
        mock_lr.return_value = mock_model
        
        result = skill.run("Train a logistic regression model", {})
        
        assert result['type'] == 'text'
        assert 'model' in result['content'].lower()
        assert result['metadata']['operation'] == 'model_training'
    
    def test_get_usage_examples(self):
        """Test usage examples"""
        skill = MLSkill()
        examples = skill.get_usage_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check for ML-specific examples
        ml_examples = [ex for ex in examples if 'model' in ex['query'].lower()]
        assert len(ml_examples) > 0

class TestDataScienceSkill:
    """Test the DataScienceSkill class"""
    
    def test_init(self):
        """Test Data Science skill initialization"""
        skill = DataScienceSkill()
        assert skill.name == "Data Science"
        assert "data_analysis" in skill.capabilities
        assert "visualization" in skill.capabilities
    
    def test_get_info(self):
        """Test getting skill information"""
        skill = DataScienceSkill()
        info = skill.get_info()
        
        assert info['name'] == "Data Science"
        assert info['description'] is not None
        assert len(info['capabilities']) > 0
    
    @patch('skills.data_science.pd.read_csv')
    def test_run_data_analysis(self, mock_read_csv):
        """Test data analysis operation"""
        skill = DataScienceSkill()
        
        # Mock pandas
        mock_data = Mock()
        mock_data.shape = (100, 5)
        mock_data.describe.return_value = Mock()
        mock_read_csv.return_value = mock_data
        
        result = skill.run("Analyze this dataset", {})
        
        assert result['type'] == 'text'
        assert 'analysis' in result['content'].lower()
        assert result['metadata']['operation'] == 'data_analysis'
    
    @patch('skills.data_science.pd.read_csv')
    @patch('skills.data_science.plt.figure')
    def test_run_visualization(self, mock_plt, mock_read_csv):
        """Test visualization operation"""
        skill = DataScienceSkill()
        
        # Mock pandas and matplotlib
        mock_data = Mock()
        mock_data.shape = (100, 5)
        mock_read_csv.return_value = mock_data
        
        mock_fig = Mock()
        mock_plt.return_value = mock_fig
        
        result = skill.run("Create a histogram", {})
        
        assert result['type'] == 'text'
        assert 'visualization' in result['content'].lower()
        assert result['metadata']['operation'] == 'visualization'
    
    def test_get_usage_examples(self):
        """Test usage examples"""
        skill = DataScienceSkill()
        examples = skill.get_usage_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check for data science-specific examples
        ds_examples = [ex for ex in examples if 'data' in ex['query'].lower() or 'analyze' in ex['query'].lower()]
        assert len(ds_examples) > 0

class TestSkillIntegration:
    """Test skill integration and common functionality"""
    
    def test_skill_consistency(self):
        """Test that all skills follow the same interface"""
        skills = [NLPSkill(), MLSkill(), DataScienceSkill()]
        
        for skill in skills:
            # All skills should have the same basic structure
            assert hasattr(skill, 'name')
            assert hasattr(skill, 'description')
            assert hasattr(skill, 'capabilities')
            assert hasattr(skill, 'run')
            assert hasattr(skill, 'get_info')
            
            # All skills should return consistent result format
            info = skill.get_info()
            assert 'name' in info
            assert 'description' in info
            assert 'capabilities' in info
    
    def test_skill_capabilities_uniqueness(self):
        """Test that skill capabilities are unique within each skill"""
        skills = [NLPSkill(), MLSkill(), DataScienceSkill()]
        
        for skill in skills:
            capabilities = skill.capabilities
            assert len(capabilities) == len(set(capabilities))  # No duplicates
    
    def test_skill_error_handling_consistency(self):
        """Test that all skills handle errors consistently"""
        skills = [NLPSkill(), MLSkill(), DataScienceSkill()]
        
        for skill in skills:
            error = Exception("Test error")
            result = skill.handle_error(error, "test query")
            
            assert result['type'] == 'error'
            assert 'error' in result['content'].lower()
            assert 'metadata' in result