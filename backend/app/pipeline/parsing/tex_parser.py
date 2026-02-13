"""
LaTeX Parser - Extract content from LaTeX (.tex) files.

Parses LaTeX source to extract:
- Document metadata (\title, \author, \date)
- Sections and subsections
- Paragraphs
- Figures (\begin{figure})
- Tables (\begin{table})
- Equations
"""

import os
import re
from typing import List
from datetime import datetime
from pathlib import Path

from app.pipeline.parsing.base_parser import BaseParser
from app.models import (
    PipelineDocument as Document,
    DocumentMetadata,
    Block,
    BlockType,
    TextStyle,
)
from app.utils.id_generator import generate_block_id


class TexParser(BaseParser):
    """Parses LaTeX (.tex) files into Document model instances."""
    
    def __init__(self):
        """Initialize the LaTeX parser."""
        self.block_counter = 0
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if this parser supports LaTeX format."""
        return file_extension.lower() in ['.tex', '.latex']
    
    def parse(self, file_path: str, document_id: str) -> Document:
        """
        Parse a LaTeX file into a Document model.
        
        Args:
            file_path: Path to the .tex file
            document_id: Unique identifier for this document
        
        Returns:
            Document instance with all extracted content
        
        Raises:
            FileNotFoundError: If LaTeX file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"LaTeX file not found: {file_path}")
        
        # Reset counters
        self.block_counter = 0
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Convert document_id to string if needed
        if not isinstance(document_id, str):
            document_id = str(document_id)
        
        # Initialize document
        document = Document(
            document_id=document_id,
            original_filename=Path(file_path).name,
            source_path=file_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Extract metadata
        document.metadata = self._extract_metadata(content)
        
        # Extract content
        blocks = self._extract_content(content)
        document.blocks = blocks
        
        # Add processing history
        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=f"Parsed LaTeX: {len(blocks)} blocks"
        )
        
        return document
    
    def _extract_metadata(self, content: str) -> DocumentMetadata:
        """Extract metadata from LaTeX preamble."""
        metadata = DocumentMetadata()
        
        # Extract title
        title_match = re.search(r'\\title\{([^}]+)\}', content)
        if title_match:
            metadata.title = self._clean_latex(title_match.group(1))
        
        # Extract author
        author_match = re.search(r'\\author\{([^}]+)\}', content)
        if author_match:
            author_text = self._clean_latex(author_match.group(1))
            metadata.authors = [a.strip() for a in author_text.split('\\and')]
        
        # Extract abstract
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            metadata.abstract = self._clean_latex(abstract_match.group(1)).strip()
        
        return metadata
    
    def _extract_content(self, content: str) -> List[Block]:
        """Extract blocks from LaTeX content."""
        blocks = []
        
        # Extract document body
        doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
        if doc_match:
            body = doc_match.group(1)
        else:
            body = content
        
        # Extract sections
        section_pattern = r'\\(section|subsection|subsubsection)\{([^}]+)\}'
        for match in re.finditer(section_pattern, body):
            section_type = match.group(1)
            section_title = self._clean_latex(match.group(2))
            
            # Determine heading level
            level_map = {'section': 1, 'subsection': 2, 'subsubsection': 3}
            level = level_map.get(section_type, 1)
            
            block_id = generate_block_id(self.block_counter)
            self.block_counter += 1
            
            block = Block(
                block_id=block_id,
                text=section_title,
                index=self.block_counter * 100,
                block_type=BlockType.UNKNOWN,
                style=TextStyle(bold=True)
            )
            block.metadata["heading_level"] = level
            block.metadata["potential_heading"] = True
            blocks.append(block)
        
        # Extract paragraphs (text between sections)
        # Remove LaTeX commands and environments
        cleaned_body = self._clean_latex(body)
        
        # Split into paragraphs
        paragraphs = cleaned_body.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:  # Skip very short fragments
                block_id = generate_block_id(self.block_counter)
                self.block_counter += 1
                
                block = Block(
                    block_id=block_id,
                    text=para,
                    index=self.block_counter * 100,
                    block_type=BlockType.UNKNOWN,
                    style=TextStyle()
                )
                blocks.append(block)
        
        return blocks
    
    def _clean_latex(self, text: str) -> str:
        """Remove LaTeX commands and keep plain text."""
        # Remove comments
        text = re.sub(r'%.*', '', text)
        
        # Remove common environments
        text = re.sub(r'\\begin\{[^}]+\}', '', text)
        text = re.sub(r'\\end\{[^}]+\}', '', text)
        
        # Remove common commands (keep their content)
        text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
        
        # Remove other commands
        text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})?', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
