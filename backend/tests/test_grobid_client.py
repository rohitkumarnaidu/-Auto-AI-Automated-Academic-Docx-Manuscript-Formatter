"""
Unit and integration tests for GROBID client.

Run with:
    pytest tests/test_grobid_client.py -v
    
Integration tests require GROBID service running:
    docker-compose up -d grobid
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

from app.pipeline.services.grobid_client import GROBIDClient, GROBIDException


# Sample TEI XML response from GROBID
SAMPLE_TEI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title level="a" type="main">Deep Learning for Academic Document Processing</title>
            </titleStmt>
            <sourceDesc>
                <biblStruct>
                    <analytic>
                        <author>
                            <persName>
                                <forename type="first">John</forename>
                                <surname>Doe</surname>
                            </persName>
                            <affiliation>
                                <orgName type="institution">MIT</orgName>
                            </affiliation>
                        </author>
                        <author>
                            <persName>
                                <forename type="first">Jane</forename>
                                <surname>Smith</surname>
                            </persName>
                            <affiliation>
                                <orgName type="institution">Stanford University</orgName>
                            </affiliation>
                        </author>
                    </analytic>
                </biblStruct>
            </sourceDesc>
        </fileDesc>
        <profileDesc>
            <abstract>
                <p>This paper presents a novel approach to document processing using deep learning.</p>
            </abstract>
            <textClass>
                <keywords>
                    <term>deep learning</term>
                    <term>document processing</term>
                    <term>NLP</term>
                </keywords>
            </textClass>
        </profileDesc>
    </teiHeader>
</TEI>
"""


class TestGROBIDClient:
    """Unit tests for GROBID client."""
    
    @pytest.fixture
    def client(self):
        """Create GROBID client instance."""
        return GROBIDClient(base_url="http://localhost:8070")
    
    def test_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "http://localhost:8070"
        assert client.timeout == 60
    
    def test_base_url_trailing_slash(self):
        """Test base URL normalization."""
        client = GROBIDClient(base_url="http://localhost:8070/")
        assert client.base_url == "http://localhost:8070"
    
    @patch('requests.get')
    def test_is_available_success(self, mock_get, client):
        """Test service availability check - success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert client.is_available() is True
        mock_get.assert_called_once_with(
            "http://localhost:8070/api/isalive",
            timeout=5
        )
    
    @patch('requests.get')
    def test_is_available_failure(self, mock_get, client):
        """Test service availability check - failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        assert client.is_available() is False
    
    def test_parse_tei_xml_complete(self, client):
        """Test TEI XML parsing with complete metadata."""
        result = client._parse_tei_xml(SAMPLE_TEI_XML)
        
        # Check title
        assert result["title"] == "Deep Learning for Academic Document Processing"
        
        # Check authors
        assert len(result["authors"]) == 2
        assert result["authors"][0]["given"] == "John"
        assert result["authors"][0]["family"] == "Doe"
        assert result["authors"][0]["full_name"] == "John Doe"
        assert result["authors"][0]["affiliation"] == "MIT"
        
        assert result["authors"][1]["given"] == "Jane"
        assert result["authors"][1]["family"] == "Smith"
        assert result["authors"][1]["affiliation"] == "Stanford University"
        
        # Check affiliations
        assert "MIT" in result["affiliations"]
        assert "Stanford University" in result["affiliations"]
        
        # Check abstract
        assert "novel approach" in result["abstract"]
        
        # Check keywords
        assert "deep learning" in result["keywords"]
        assert "NLP" in result["keywords"]
        
        # Check metadata
        assert result["source"] == "grobid"
        assert result["confidence"] > 0.8
    
    def test_parse_tei_xml_minimal(self, client):
        """Test TEI XML parsing with minimal metadata."""
        minimal_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
            <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <title level="a" type="main">Test Title</title>
                    </titleStmt>
                </fileDesc>
            </teiHeader>
        </TEI>
        """
        
        result = client._parse_tei_xml(minimal_xml)
        
        assert result["title"] == "Test Title"
        assert result["authors"] == []
        assert result["affiliations"] == []
        assert result["abstract"] == ""
        assert result["keywords"] == []
        assert result["confidence"] < 0.5  # Low confidence due to missing data
    
    def test_parse_tei_xml_invalid(self, client):
        """Test TEI XML parsing with invalid XML."""
        invalid_xml = "This is not XML"
        
        result = client._parse_tei_xml(invalid_xml)
        
        # Should return empty metadata
        assert result["title"] == ""
        assert result["authors"] == []
        assert result["confidence"] == 0.0
    
    def test_calculate_confidence_high(self, client):
        """Test confidence calculation - high confidence."""
        title = "A Comprehensive Study of Deep Learning"
        authors = [
            {"given": "John", "family": "Doe"},
            {"given": "Jane", "family": "Smith"}
        ]
        
        confidence = client._calculate_confidence(title, authors)
        
        assert confidence >= 0.8
    
    def test_calculate_confidence_low(self, client):
        """Test confidence calculation - low confidence."""
        title = ""
        authors = []
        
        confidence = client._calculate_confidence(title, authors)
        
        assert confidence <= 0.3
    
    def test_empty_metadata(self, client):
        """Test empty metadata structure."""
        result = client._empty_metadata()
        
        assert result["title"] == ""
        assert result["authors"] == []
        assert result["affiliations"] == []
        assert result["abstract"] == ""
        assert result["keywords"] == []
        assert result["confidence"] == 0.0
        assert result["source"] == "grobid"


class TestGROBIDIntegration:
    """Integration tests requiring GROBID service."""
    
    @pytest.fixture
    def client(self):
        """Create GROBID client for integration tests."""
        return GROBIDClient(base_url="http://localhost:8070")
    
    @pytest.mark.integration
    def test_service_availability(self, client):
        """Test GROBID service is running."""
        if not client.is_available():
            pytest.skip("GROBID service not running. Start with: docker-compose up -d grobid")
        
        assert client.is_available() is True
    
    @pytest.mark.integration
    def test_extract_metadata_pdf(self, client, tmp_path):
        """Test metadata extraction from PDF (requires sample file)."""
        # This test requires a sample PDF file
        # Skip if GROBID not available
        if not client.is_available():
            pytest.skip("GROBID service not running")
        
        # TODO: Add sample PDF file to tests/fixtures/
        # sample_pdf = Path("tests/fixtures/sample_paper.pdf")
        # if not sample_pdf.exists():
        #     pytest.skip("Sample PDF not found")
        # 
        # result = client.extract_metadata(str(sample_pdf))
        # 
        # assert result["title"]
        # assert len(result["authors"]) > 0
        # assert result["confidence"] > 0.5
        
        pytest.skip("Sample PDF fixture not yet added")
    
    @pytest.mark.integration
    def test_extract_metadata_service_unavailable(self):
        """Test error handling when service is unavailable."""
        client = GROBIDClient(base_url="http://localhost:9999")  # Wrong port
        
        with pytest.raises(GROBIDException, match="not available"):
            client.extract_metadata("dummy.pdf")


# Pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires GROBID service)"
    )
