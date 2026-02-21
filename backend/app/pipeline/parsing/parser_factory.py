"""
Parser Factory - Automatically select the correct parser for a given file format.

This factory pattern allows the pipeline to support multiple input formats
without hardcoding parser selection logic throughout the codebase.
"""

import os
from typing import Optional

from app.pipeline.parsing.base_parser import BaseParser
from app.pipeline.parsing.parser import DocxParser
from app.pipeline.parsing.pdf_parser import PdfParser
from app.pipeline.parsing.txt_parser import TxtParser
from app.pipeline.parsing.html_parser import HtmlParser
from app.pipeline.parsing.md_parser import MarkdownParser
from app.pipeline.parsing.tex_parser import TexParser
from app.pipeline.safety import safe_function


class ParserFactory:
    """Factory to create the appropriate parser for a given file format."""
    
    def __init__(self):
        """Initialize the factory with all available parsers."""
        # Try to initialize all parsers (some may fail if dependencies missing)
        self.parsers = []
        
        # DOCX parser (always available - core functionality)
        try:
            self.parsers.append(DocxParser())
        except Exception as e:
            print(f"Warning: DocxParser initialization failed: {e}")
        
        # Nougat PDF parser — PRIMARY for academic PDFs (Meta AI neural model)
        # Must be registered BEFORE PdfParser so it takes priority for .pdf files
        try:
            from app.pipeline.parsing.nougat_parser import NougatParser
            self.parsers.append(NougatParser())
            print("Info: NougatParser (Meta AI) registered as primary PDF parser.")
        except ImportError:
            print("Info: Nougat not available (install with: pip install nougat-ocr). Using PyMuPDF for PDFs.")
        except Exception as e:
            print(f"Warning: NougatParser initialization failed: {e}. Falling back to PyMuPDF.")
        
        # PDF parser — FALLBACK (requires PyMuPDF)
        try:
            self.parsers.append(PdfParser())
        except ImportError:
            print("Info: PDF parsing not available (install PyMuPDF: pip install PyMuPDF)")
        except Exception as e:
            print(f"Warning: PdfParser initialization failed: {e}")
        
        # Plain text parser (always available)
        try:
            self.parsers.append(TxtParser())
        except Exception as e:
            print(f"Warning: TxtParser initialization failed: {e}")
        
        # HTML parser (requires BeautifulSoup4)
        try:
            self.parsers.append(HtmlParser())
        except ImportError:
            print("Info: HTML parsing not available (install beautifulsoup4: pip install beautifulsoup4)")
        except Exception as e:
            print(f"Warning: HtmlParser initialization failed: {e}")
            
        # Markdown parser (always available)
        try:
            self.parsers.append(MarkdownParser())
        except Exception as e:
            print(f"Warning: MarkdownParser initialization failed: {e}")
            
        # TeX parser (always available)
        try:
            self.parsers.append(TexParser())
        except Exception as e:
            print(f"Warning: TexParser initialization failed: {e}")

    @safe_function(fallback_value=None, error_message="ParserFactory.get_parser failed")
    def get_parser(self, file_path: str) -> Optional[BaseParser]:
        """
        Get the appropriate parser for the given file.
        
        Args:
            file_path: Path to the input file
        
        Returns:
            Parser instance that can handle the file format
        
        Raises:
            ValueError: If no parser supports the file format
        """
        # Extract file extension
        _, ext = os.path.splitext(file_path)
        file_ext = ext.lower()

        # Find matching parser
        for parser in self.parsers:
            if parser.supports_format(file_ext):
                return parser
        
        # No parser found - raise ValueError
        supported_formats = set()
        for parser in self.parsers:
            # Get supported formats from each parser
            for ext in ['.docx', '.pdf', '.txt', '.html', '.htm', '.md', '.markdown', '.tex', '.latex', '.doc']:
                if parser.supports_format(ext):
                    supported_formats.add(ext)
        
        raise ValueError(
            f"No parser available for file format '{file_ext}'. "
            f"Supported formats: {', '.join(sorted(supported_formats))}"
        )
    
    def get_supported_formats(self) -> list:
        """
        Get list of all supported file formats.
        
        Returns:
            List of file extensions (e.g., ['.docx', '.pdf', '.txt'])
        """
        supported = set()
        for parser in self.parsers:
            for ext in ['.docx', '.pdf', '.txt', '.html', '.htm', '.md', '.markdown', '.tex', '.latex', '.doc']:
                if parser.supports_format(ext):
                    supported.add(ext)
        return sorted(supported)
