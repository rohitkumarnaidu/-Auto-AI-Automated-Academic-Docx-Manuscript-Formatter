
import pytest
import time
import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.pipeline.orchestrator import PipelineOrchestrator

def log(msg):
    print(f"\n[INTEGRATION] {msg}")

@pytest.mark.integration
class TestEndToEndIntegration:
    """
    End-to-End Integration Tests for Manuscript Formatter Pipeline.
    Simplified version for stdout capture.
    """
    
    @pytest.fixture(scope="class")
    def samples_dir(self):
        return Path("samples")
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock SQLAlchemy session to capture DB updates without real DB."""
        with patch("app.pipeline.orchestrator.SessionLocal") as mock_session_cls:
            mock_session = MagicMock()
            mock_session_cls.return_value = mock_session
            mock_session.__enter__.return_value = mock_session
            
            # Mock Document record
            mock_doc_rec = MagicMock()
            mock_doc_rec.status = "PENDING"
            mock_doc_rec.output_path = None
            
            # Mock query().filter_by().first()
            mock_session.query.return_value.filter_by.return_value.first.return_value = mock_doc_rec
            
            yield mock_session, mock_doc_rec

    @pytest.fixture
    def orchestrator(self):
        return PipelineOrchestrator(templates_dir="app/templates", temp_dir="temp")

    def test_samples_exist(self, samples_dir):
        """Verify sample PDFs availability."""
        pdf_files = list(samples_dir.glob("*.pdf"))
        log(f"Checking for samples in {samples_dir.absolute()}")
        assert len(pdf_files) > 0, "No sample PDFs found in 'samples/' directory."
        log(f"Found {len(pdf_files)} sample PDFs.")

    def test_end_to_end_pipeline(self, orchestrator, samples_dir, mock_db_session):
        """Run full pipeline and measure performance."""
        mock_session, mock_doc_rec = mock_db_session
        pdf_files = list(samples_dir.glob("*.pdf"))[:2]
        
        if not pdf_files:
            pytest.skip("No samples to test")
            
        success_count = 0
        total_time = 0
        
        log("="*60)
        log("STARTING END-TO-END PIPELINE PERFORMANCE TEST")
        log("="*60)
        
        for i, pdf_path in enumerate(pdf_files):
            log(f"Processing {pdf_path.name}...")
            start_time = time.time()
            
            try:
                # Orchestrator run
                response = orchestrator.run_pipeline(
                    input_path=str(pdf_path.absolute()),
                    job_id=str(uuid.uuid4()),
                    template_name="IEEE"
                )
                
                duration = time.time() - start_time
                total_time += duration
                log(f"SUCCESS: {pdf_path.name} processed in {duration:.2f}s")
                log(f"Response Status: {response['status']}")
                
                assert response["status"] == "success"
                success_count += 1
            except Exception as e:
                log(f"FAILURE: {pdf_path.name} error: {str(e)}")
                raise e

        avg_time = total_time / success_count if success_count > 0 else 0
        log("="*60)
        log(f"PERFORMANCE SUMMARY: Average Time: {avg_time:.2f}s per file")
        log(f"Success Rate: {success_count}/{len(pdf_files)}")
        log("="*60)
        
        assert avg_time < 15.0, f"Average processing time {avg_time:.2f}s exceeds 15s target"
        assert success_count == len(pdf_files)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
