"""
SciBERT Semantic Parser Tests
Tests NLP classification and semantic analysis.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

class TestSemanticParser:
    """Test suite for SciBERT semantic parser."""
    
    @pytest.mark.unit
    def test_parser_initialization(self):
        """Test semantic parser can be initialized."""
        with patch('app.pipeline.intelligence.semantic_parser.AutoTokenizer') as mock_tokenizer:
            with patch('app.pipeline.intelligence.semantic_parser.AutoModel') as mock_model:
                from app.pipeline.intelligence.semantic_parser import SemanticParser
                
                parser = SemanticParser()
                assert parser is not None
    
    @pytest.mark.unit
    def test_model_loading(self):
        """Test SciBERT model loading."""
        with patch('app.pipeline.intelligence.semantic_parser.AutoTokenizer') as mock_tokenizer:
            with patch('app.pipeline.intelligence.semantic_parser.AutoModel') as mock_model:
                from app.pipeline.intelligence.semantic_parser import SemanticParser
                
                parser = SemanticParser()
                parser._load_model()
                
                # Verify model and tokenizer were loaded
                assert parser.tokenizer is not None
                assert parser.model is not None
    
    @pytest.mark.unit
    def test_singleton_pattern(self):
        """Test get_semantic_parser returns singleton."""
        with patch('app.pipeline.intelligence.semantic_parser.AutoTokenizer'):
            with patch('app.pipeline.intelligence.semantic_parser.AutoModel'):
                from app.pipeline.intelligence.semantic_parser import get_semantic_parser
                
                parser1 = get_semantic_parser()
                parser2 = get_semantic_parser()
                
                # Should be same instance
                assert parser1 is parser2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
