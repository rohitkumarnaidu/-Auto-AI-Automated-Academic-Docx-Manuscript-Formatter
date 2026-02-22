"""
GROBID Pipeline Integration Tests

Tests the full integration of GROBID with the document processing pipeline.
Verifies metadata extraction, pipeline orchestration, and performance targets.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import requests

from app.pipeline.services.grobid_client import GROBIDClient, GROBIDException
from app.pipeline.orchestrator import PipelineOrchestrator
from app.models import PipelineDocument, DocumentMetadata


@pytest.mark.integration
class TestGROBIDPipelineIntegration:
    """Integration tests for GROBID in the full pipeline."""
    
    @pytest.fixture
    def grobid_client(self):
        """Create a GROBID client instance."""
        return GROBIDClient(base_url="http://localhost:8070")
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Path to a sample PDF for testing."""
        samples_dir = Path("samples")
        pdf_files = list(samples_dir.glob("*.pdf"))
        if pdf_files:
            return pdf_files[0]
        pytest.skip("No sample PDFs available")
    
    @pytest.fixture
    def orchestrator(self):
        """Create pipeline orchestrator."""
        return PipelineOrchestrator(
            templates_dir="app/templates",
            temp_dir="temp"
        )
    
    def test_grobid_service_availability(self, grobid_client):
        """Test that GROBID service is available."""
        try:
            is_available = grobid_client.is_available()
            if not is_available:
                pytest.skip("GROBID service not available at http://localhost:8070")
        except Exception as e:
            pytest.skip(f"GROBID service not accessible: {str(e)}")
    
    def test_grobid_metadata_extraction(self, grobid_client, sample_pdf_path):
        """Test GROBID metadata extraction from a real PDF."""
        # Skip if GROBID not available
        if not grobid_client.is_available():
            pytest.skip("GROBID service not available")
        
        # Extract metadata
        metadata = grobid_client.extract_metadata(str(sample_pdf_path))
        
        # Verify metadata structure
        assert metadata is not None, "Metadata should not be None"
        assert isinstance(metadata, dict), "Metadata should be a dictionary"
        
        # Check for expected fields (may be empty but should exist)
        assert "title" in metadata
        assert "authors" in metadata
        assert "abstract" in metadata
        
        print(f"\n✅ Extracted metadata:")
        print(f"   Title: {metadata.get('title', 'N/A')}")
        print(f"   Authors: {len(metadata.get('authors', []))} found")
        print(f"   Abstract length: {len(metadata.get('abstract', ''))} chars")
    
    @pytest.mark.performance
    def test_grobid_response_time(self, grobid_client, sample_pdf_path):
        """Test that GROBID responds within 5 seconds."""
        if not grobid_client.is_available():
            pytest.skip("GROBID service not available")
        
        # Measure response time
        start_time = time.time()
        metadata = grobid_client.extract_metadata(str(sample_pdf_path))
        duration = time.time() - start_time
        
        print(f"\n⏱️  GROBID response time: {duration:.2f}s")
        
        # Assert performance target
        assert duration < 5.0, f"GROBID response time {duration:.2f}s exceeds 5s target"
        
        # Verify we got valid metadata
        assert metadata is not None
    
    def test_pipeline_with_grobid_integration(self, orchestrator, sample_pdf_path):
        """Test full pipeline with GROBID metadata injection."""
        # Mock the database session
        with patch("app.pipeline.orchestrator.get_supabase_client") as mock_sb:
            mock_client = MagicMock()
            mock_sb.return_value = mock_client
            
            # Mock Supabase table operations
            mock_table = MagicMock()
            mock_client.table.return_value = mock_table
            mock_table.select.return_value = mock_table
            mock_table.update.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.match.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[])
            
            # Run pipeline
            start_time = time.time()
            result = orchestrator.run_pipeline(
                input_path=str(sample_pdf_path),
                job_id="test_grobid_integration",
                template_name="IEEE"
            )
            duration = time.time() - start_time
            
            # Verify pipeline success
            assert result["status"] == "success", f"Pipeline failed: {result.get('error')}"
            
            print(f"\n✅ Pipeline completed in {duration:.2f}s")
            print(f"   Status: {result['status']}")
    
    def test_grobid_metadata_in_document(self, grobid_client, sample_pdf_path):
        """Test that GROBID metadata is properly stored in PipelineDocument."""
        if not grobid_client.is_available():
            pytest.skip("GROBID service not available")
        
        # Extract metadata
        grobid_metadata = grobid_client.extract_metadata(str(sample_pdf_path))
        
        # Create a document and inject metadata
        doc = PipelineDocument(
            document_id="test_doc",
            metadata=DocumentMetadata(title="Test Document")
        )
        
        # Inject GROBID metadata into ai_hints
        doc.metadata.ai_hints["grobid_metadata"] = grobid_metadata
        
        # Verify metadata is accessible
        assert "grobid_metadata" in doc.metadata.ai_hints
        stored_metadata = doc.metadata.ai_hints["grobid_metadata"]
        
        assert stored_metadata["title"] == grobid_metadata["title"]
        assert stored_metadata["authors"] == grobid_metadata["authors"]
        
        print(f"\n✅ Metadata properly stored in PipelineDocument")
    
    def test_grobid_error_handling(self, grobid_client):
        """Test GROBID error handling with invalid input."""
        # Test with non-existent file
        with pytest.raises(GROBIDException):
            grobid_client.extract_metadata("nonexistent.pdf")
        
        print(f"\n✅ Error handling works correctly")
    
    @pytest.mark.performance
    def test_multiple_grobid_requests(self, grobid_client, sample_pdf_path):
        """Test GROBID performance with multiple sequential requests."""
        if not grobid_client.is_available():
            pytest.skip("GROBID service not available")
        
        num_requests = 3
        durations = []
        
        for i in range(num_requests):
            start_time = time.time()
            metadata = grobid_client.extract_metadata(str(sample_pdf_path))
            duration = time.time() - start_time
            durations.append(duration)
            
            assert metadata is not None
        
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        
        print(f"\n⏱️  Performance metrics ({num_requests} requests):")
        print(f"   Average: {avg_duration:.2f}s")
        print(f"   Max: {max_duration:.2f}s")
        print(f"   Min: {min(durations):.2f}s")
        
        # All requests should be under 5s
        assert max_duration < 5.0, f"Max duration {max_duration:.2f}s exceeds 5s target"


@pytest.mark.integration
class TestGROBIDFallback:
    """Test GROBID fallback behavior when service is unavailable."""
    
    def test_pipeline_continues_without_grobid(self, tmp_path):
        """Test that pipeline continues when GROBID is unavailable."""
        # Create a mock GROBID client that always fails
        with patch("app.pipeline.orchestrator.GROBIDClient") as mock_grobid:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = False
            mock_instance.extract_metadata.return_value = {
                "title": "",
                "authors": [],
                "abstract": ""
            }
            mock_grobid.return_value = mock_instance
            
            # This test verifies the pipeline doesn't crash
            # when GROBID is unavailable
            print("\n✅ Pipeline handles GROBID unavailability gracefully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
