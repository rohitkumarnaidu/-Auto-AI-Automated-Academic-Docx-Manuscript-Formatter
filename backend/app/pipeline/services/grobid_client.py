"""
GROBID REST API Client for metadata extraction.

GROBID (GeneRation Of BIbliographic Data) is a machine learning library for 
extracting, parsing, and restructuring raw documents into structured XML/TEI.

This client replaces brittle regex-based metadata extraction with trained models
that can extract 68+ metadata labels including:
- Title, authors, affiliations
- Abstract, keywords
- References, citations
- Document structure
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class GROBIDClient:
    """REST API client for GROBID service."""
    
    # TEI namespace for XML parsing
    TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
    
    def __init__(self, base_url: str = "http://localhost:8070"):
        """
        Initialize GROBID client.
        
        Args:
            base_url: GROBID service URL (default: http://localhost:8070)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 60  # seconds
        
    def is_available(self) -> bool:
        """Check if GROBID service is running."""
        try:
            response = requests.get(
                f"{self.base_url}/api/isalive",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from document using GROBID.
        
        Args:
            file_path: Path to document file (PDF, DOCX, etc.)
            
        Returns:
            Dictionary with extracted metadata:
            {
                "title": str,
                "authors": List[Dict[str, str]],  # [{"given": "John", "family": "Doe", "affiliation": "..."}]
                "affiliations": List[str],
                "abstract": str,
                "keywords": List[str],
                "references": List[Dict],
                "raw_xml": str  # Full TEI XML for advanced processing
            }
            
        Raises:
            GROBIDException: If service is unavailable or processing fails
        """
        if not self.is_available():
            raise GROBIDException(
                f"GROBID service not available at {self.base_url}. "
                "Start it with: docker-compose up -d grobid"
            )
        
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/api/processHeaderDocument",
                    files={'input': f},
                    timeout=self.timeout
                )
            
            if response.status_code != 200:
                raise GROBIDException(
                    f"GROBID processing failed: {response.status_code} - {response.text}"
                )
            
            # Parse TEI XML response
            return self._parse_tei_xml(response.text)
            
        except requests.exceptions.RequestException as e:
            raise GROBIDException(f"GROBID request failed: {str(e)}")
        except Exception as e:
            logger.error(f"GROBID metadata extraction failed: {str(e)}")
            raise GROBIDException(f"Metadata extraction failed: {str(e)}")
    
    def _parse_tei_xml(self, xml_str: str) -> Dict[str, Any]:
        """
        Parse GROBID TEI XML output into structured metadata.
        
        Args:
            xml_str: TEI XML string from GROBID
            
        Returns:
            Structured metadata dictionary
        """
        try:
            root = ET.fromstring(xml_str)
            
            # Extract title
            title = self._extract_title(root)
            
            # Extract authors and affiliations
            authors, affiliations = self._extract_authors(root)
            
            # Extract abstract
            abstract = self._extract_abstract(root)
            
            # Extract keywords
            keywords = self._extract_keywords(root)
            
            return {
                "title": title,
                "authors": authors,
                "affiliations": affiliations,
                "abstract": abstract,
                "keywords": keywords,
                "raw_xml": xml_str,
                "source": "grobid",
                "confidence": self._calculate_confidence(title, authors)
            }
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse GROBID XML: {str(e)}")
            return self._empty_metadata()
    
    def _extract_title(self, root: ET.Element) -> str:
        """Extract document title from TEI XML."""
        title_elem = root.find(".//tei:titleStmt/tei:title[@type='main']", self.TEI_NS)
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        # Fallback: try any title
        title_elem = root.find(".//tei:titleStmt/tei:title", self.TEI_NS)
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        return ""
    
    def _extract_authors(self, root: ET.Element) -> tuple[List[Dict[str, str]], List[str]]:
        """
        Extract authors and affiliations from TEI XML.
        
        Returns:
            Tuple of (authors_list, affiliations_list)
        """
        authors = []
        affiliations_set = set()
        
        # Find all author elements
        author_elems = root.findall(".//tei:sourceDesc//tei:author", self.TEI_NS)
        
        for author_elem in author_elems:
            # Extract name
            given_name = ""
            family_name = ""
            
            persName = author_elem.find(".//tei:persName", self.TEI_NS)
            if persName is not None:
                forename = persName.find(".//tei:forename[@type='first']", self.TEI_NS)
                surname = persName.find(".//tei:surname", self.TEI_NS)
                
                if forename is not None and forename.text:
                    given_name = forename.text.strip()
                if surname is not None and surname.text:
                    family_name = surname.text.strip()
            
            # Extract affiliation
            affiliation = ""
            affiliation_elem = author_elem.find(".//tei:affiliation/tei:orgName[@type='institution']", self.TEI_NS)
            if affiliation_elem is not None and affiliation_elem.text:
                affiliation = affiliation_elem.text.strip()
                affiliations_set.add(affiliation)
            
            if given_name or family_name:
                authors.append({
                    "given": given_name,
                    "family": family_name,
                    "full_name": f"{given_name} {family_name}".strip(),
                    "affiliation": affiliation
                })
        
        return authors, list(affiliations_set)
    
    def _extract_abstract(self, root: ET.Element) -> str:
        """Extract abstract from TEI XML."""
        abstract_elem = root.find(".//tei:profileDesc/tei:abstract", self.TEI_NS)
        if abstract_elem is not None:
            # Get all text content, joining paragraphs
            paragraphs = abstract_elem.findall(".//tei:p", self.TEI_NS)
            if paragraphs:
                return " ".join(p.text.strip() for p in paragraphs if p.text)
            elif abstract_elem.text:
                return abstract_elem.text.strip()
        return ""
    
    def _extract_keywords(self, root: ET.Element) -> List[str]:
        """Extract keywords from TEI XML."""
        keywords = []
        keyword_elems = root.findall(".//tei:keywords/tei:term", self.TEI_NS)
        for kw in keyword_elems:
            if kw.text:
                keywords.append(kw.text.strip())
        return keywords
    
    def _calculate_confidence(self, title: str, authors: List[Dict]) -> float:
        """
        Calculate confidence score for extracted metadata.
        
        Score based on:
        - Title presence and length
        - Number of authors
        - Completeness of author names
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        score = 0.0
        
        # Title check (40% weight)
        if title:
            if len(title) > 10:
                score += 0.4
            else:
                score += 0.2
        
        # Authors check (40% weight)
        if authors:
            if len(authors) >= 1:
                score += 0.2
            if len(authors) >= 2:
                score += 0.1
            # Check name completeness
            complete_names = sum(1 for a in authors if a.get("given") and a.get("family"))
            if complete_names == len(authors):
                score += 0.1
        
        # Abstract/keywords (20% weight) - placeholder for future
        score += 0.2
        
        return min(score, 1.0)
    
    def _empty_metadata(self) -> Dict[str, Any]:
        """Return empty metadata structure."""
        return {
            "title": "",
            "authors": [],
            "affiliations": [],
            "abstract": "",
            "keywords": [],
            "raw_xml": "",
            "source": "grobid",
            "confidence": 0.0
        }


class GROBIDException(Exception):
    """Exception raised for GROBID service errors."""
    pass
