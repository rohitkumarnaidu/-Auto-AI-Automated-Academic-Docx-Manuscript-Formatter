"""
Tests for the LangChain document agent.
"""
import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
from app.pipeline.agents.document_agent import DocumentAgent
from app.pipeline.agents.tools.metadata_tool import MetadataExtractionTool
from app.pipeline.agents.tools.layout_tool import LayoutAnalysisTool
from app.pipeline.agents.tools.validation_tool import ValidationTool
from app.models import PipelineDocument, DocumentMetadata
from app.pipeline.orchestrator_v2 import AgentOrchestrator


class TestMetadataExtractionTool:
    """Test the metadata extraction tool."""
    
    @patch('app.pipeline.agents.tools.metadata_tool.GROBIDClient')
    def test_metadata_tool_success(self, mock_grobid_class):
        """Test successful metadata extraction."""
        # Mock GROBID client
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.extract_metadata.return_value = {
            "title": "Test Paper",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This is a test abstract.",
            "references": [{"title": "Ref 1"}]
        }
        mock_grobid_class.return_value = mock_client
        
        # Create and run tool
        tool = MetadataExtractionTool()
        result = tool._run("test.pdf")
        
        # Verify
        assert "success" in result
        assert "Test Paper" in result
        assert "John Doe" in result
        mock_client.extract_metadata.assert_called_once_with("test.pdf")
    
    @patch('app.pipeline.agents.tools.metadata_tool.GROBIDClient')
    def test_metadata_tool_service_unavailable(self, mock_grobid_class):
        """Test when GROBID service is unavailable."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = False
        mock_grobid_class.return_value = mock_client
        
        tool = MetadataExtractionTool()
        result = tool._run("test.pdf")
        
        assert "ERROR" in result
        assert "not available" in result


class TestLayoutAnalysisTool:
    """Test the layout analysis tool."""
    
    @patch('app.pipeline.agents.tools.layout_tool.DoclingClient')
    def test_layout_tool_success(self, mock_docling_class):
        """Test successful layout analysis."""
        mock_client = MagicMock()
        mock_client.analyze_layout.return_value = {
            "blocks": [
                {"block_type": "heading_1", "text": "Introduction", "font_size": 16},
                {"block_type": "paragraph", "text": "This is content.", "font_size": 12},
                {"block_type": "figure", "text": "Figure 1"}
            ]
        }
        mock_docling_class.return_value = mock_client
        
        tool = LayoutAnalysisTool()
        result = tool._run("test.pdf")
        
        assert "success" in result
        assert "total_blocks" in result
        assert "has_figures" in result
        mock_client.analyze_layout.assert_called_once_with("test.pdf")
    
    @patch('app.pipeline.agents.tools.layout_tool.DoclingClient')
    def test_layout_tool_failure(self, mock_docling_class):
        """Test layout analysis failure."""
        mock_client = MagicMock()
        mock_client.analyze_layout.side_effect = Exception("Analysis failed")
        mock_docling_class.return_value = mock_client
        
        tool = LayoutAnalysisTool()
        result = tool._run("test.pdf")
        
        assert "ERROR" in result
        assert "failed" in result


class TestValidationTool:
    """Test the validation tool."""
    
    def test_validation_tool_success(self):
        """Test successful document validation."""
        # Create test document
        doc = PipelineDocument(
            document_id="test_123",
            metadata=DocumentMetadata(
                title="Test Document",
                authors=["Author One"],
                abstract="Test abstract"
            )
        )
        
        # Create tool and set document
        tool = ValidationTool()
        tool.set_document("test_123", doc)
        
        # Run validation
        result = tool._run("test_123")
        
        assert "success" in result
        assert "validation" in result
        assert "is_valid" in result
    
    def test_validation_tool_document_not_found(self):
        """Test validation when document is not cached."""
        tool = ValidationTool()
        result = tool._run("nonexistent_id")
        
        assert "ERROR" in result
        assert "not found" in result


class TestDocumentAgent:
    """Test the document agent."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Mock environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    
    @patch('app.pipeline.agents.document_agent.ChatOpenAI')
    @patch('app.pipeline.agents.document_agent.create_openai_functions_agent')
    @patch('app.pipeline.agents.document_agent.AgentExecutor')
    def test_agent_initialization(self, mock_executor_class, mock_create_agent, mock_llm_class, mock_env):
        """Test agent initialization."""
        agent = DocumentAgent()
        
        # Verify LLM was created
        mock_llm_class.assert_called_once()
        
        # Verify agent was created with tools
        assert mock_create_agent.called
        call_kwargs = mock_create_agent.call_args[1]
        assert 'tools' in call_kwargs
        assert len(call_kwargs['tools']) == 3  # metadata, layout, validation
    
    @patch('app.pipeline.agents.document_agent.ChatOpenAI')
    @patch('app.pipeline.agents.document_agent.create_openai_functions_agent')
    @patch('app.pipeline.agents.document_agent.AgentExecutor')
    def test_agent_process_document(self, mock_executor_class, mock_create_agent, mock_llm_class, mock_env):
        """Test document processing with agent."""
        # Mock executor
        mock_executor = MagicMock()
        mock_executor.invoke.return_value = {
            "output": "Document analyzed successfully",
            "intermediate_steps": [
                (MagicMock(), '{"status": "success"}'),
                (MagicMock(), '{"status": "success"}')
            ]
        }
        mock_executor_class.return_value = mock_executor
        
        # Create agent and process
        agent = DocumentAgent()
        result = agent.process_document("test.pdf")
        
        # Verify
        assert result["success"] is True
        assert "analysis" in result
        assert "should_fallback" in result
        assert result["should_fallback"] is False
    
    @patch('app.pipeline.agents.document_agent.ChatOpenAI')
    @patch('app.pipeline.agents.document_agent.create_openai_functions_agent')
    @patch('app.pipeline.agents.document_agent.AgentExecutor')
    def test_agent_retry_logic(self, mock_executor_class, mock_create_agent, mock_llm_class, mock_env):
        """Test agent retry logic on failure."""
        # Mock executor to fail twice then succeed
        mock_executor = MagicMock()
        mock_executor.invoke.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            {"output": "Success on third try", "intermediate_steps": []}
        ]
        mock_executor_class.return_value = mock_executor
        
        agent = DocumentAgent(max_retries=3)
        result = agent.process_document("test.pdf")
        
        # Verify retries occurred
        assert mock_executor.invoke.call_count == 3
        assert result["success"] is True


class TestAgentOrchestrator:
    """Test the agent orchestrator with fallback."""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    @patch('app.pipeline.orchestrator_v2.LegacyOrchestrator')
    def test_orchestrator_fallback_no_api_key(self, mock_legacy_class):
        """Test fallback when no API key is set."""
        mock_legacy = MagicMock()
        mock_legacy_class.return_value = mock_legacy
        
        orchestrator = AgentOrchestrator(use_agent=True)
        
        # Should fallback to legacy
        assert orchestrator.use_agent is False
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('app.pipeline.orchestrator_v2.DocumentAgent')
    @patch('app.pipeline.orchestrator_v2.LegacyOrchestrator')
    def test_orchestrator_agent_success(self, mock_legacy_class, mock_agent_class):
        """Test successful agent orchestration."""
        # Mock agent
        mock_agent = MagicMock()
        mock_agent.process_document.return_value = {
            "success": True,
            "should_fallback": False,
            "analysis": "Document processed successfully"
        }
        mock_agent_class.return_value = mock_agent
        
        # Mock legacy orchestrator
        mock_legacy = MagicMock()
        processed_doc = PipelineDocument(document_id="test")
        mock_legacy.process.return_value = processed_doc
        mock_legacy_class.return_value = mock_legacy
        
        # Create orchestrator and process
        orchestrator = AgentOrchestrator(use_agent=True)
        doc = PipelineDocument(document_id="test", source_path="test.pdf")
        result = orchestrator.process(doc)
        
        # Verify agent was called
        mock_agent.process_document.assert_called_once()
        
        # Verify legacy was still used for actual processing (hybrid approach)
        mock_legacy.process.assert_called_once()
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('app.pipeline.orchestrator_v2.DocumentAgent')
    @patch('app.pipeline.orchestrator_v2.LegacyOrchestrator')
    def test_orchestrator_agent_recommends_fallback(self, mock_legacy_class, mock_agent_class):
        """Test fallback when agent recommends it."""
        # Mock agent recommending fallback
        mock_agent = MagicMock()
        mock_agent.process_document.return_value = {
            "success": True,
            "should_fallback": True,
            "analysis": "Too many errors, recommend fallback"
        }
        mock_agent_class.return_value = mock_agent
        
        # Mock legacy orchestrator
        mock_legacy = MagicMock()
        processed_doc = PipelineDocument(document_id="test")
        mock_legacy.process.return_value = processed_doc
        mock_legacy_class.return_value = mock_legacy
        
        orchestrator = AgentOrchestrator(use_agent=True)
        doc = PipelineDocument(document_id="test", source_path="test.pdf")
        result = orchestrator.process(doc)
        
        # Verify fallback was used
        mock_legacy.process.assert_called_once()
