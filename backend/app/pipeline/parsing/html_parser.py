"""
HTML Parser - Extract content from HTML files.

Uses BeautifulSoup to parse HTML and extract:
- Headings (h1, h2, h3, etc.)
- Paragraphs
- Images
- Tables
- Lists
"""

import os
from typing import List, Tuple
from datetime import datetime
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from app.pipeline.parsing.base_parser import BaseParser
from app.models import (
    PipelineDocument as Document,
    DocumentMetadata,
    Block,
    BlockType,
    TextStyle,
    Figure,
    ImageFormat,
)
from app.utils.id_generator import generate_block_id, generate_figure_id


class HtmlParser(BaseParser):
    """Parses HTML files into Document model instances."""
    
    def __init__(self):
        """Initialize the HTML parser."""
        if not BS4_AVAILABLE:
            raise ImportError(
                "BeautifulSoup4 is required for HTML parsing. Install with: pip install beautifulsoup4"
            )
        self.block_counter = 0
        self.figure_counter = 0
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if this parser supports HTML format."""
        return file_extension.lower() in ['.html', '.htm']
    
    def parse(self, file_path: str, document_id: str) -> Document:
        """
        Parse an HTML file into a Document model.
        
        Args:
            file_path: Path to the .html file
            document_id: Unique identifier for this document
        
        Returns:
            Document instance with all extracted content
        
        Raises:
            FileNotFoundError: If HTML file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HTML file not found: {file_path}")
        
        # Reset counters
        self.block_counter = 0
        self.figure_counter = 0
        
        # Read and parse HTML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                soup = BeautifulSoup(f, 'html.parser')
        
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
        document.metadata = self._extract_metadata(soup)
        
        # Extract content
        blocks, figures = self._extract_content(soup)
        
        document.blocks = blocks
        document.figures = figures
        
        # Add processing history
        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=f"Parsed HTML: {len(blocks)} blocks, {len(figures)} figures"
        )
        
        return document
    
    def _extract_metadata(self, soup) -> DocumentMetadata:
        """Extract metadata from HTML head."""
        metadata = DocumentMetadata()
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata.title = title_tag.get_text().strip()
        
        # Extract meta tags
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            metadata.authors = [meta_author['content']]
        
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and meta_description.get('content'):
            metadata.abstract = meta_description['content']
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            metadata.keywords = [k.strip() for k in meta_keywords['content'].split(',')]
        
        return metadata
    
    def _extract_content(self, soup) -> Tuple[List[Block], List[Figure]]:
        """Extract blocks and figures from HTML body."""
        blocks = []
        figures = []
        
        # Find body or use whole document
        body = soup.find('body') or soup
        
        # Extract content in order
        for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'img']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Heading
                text = element.get_text().strip()
                if text:
                    block_id = generate_block_id(self.block_counter)
                    self.block_counter += 1
                    
                    level = int(element.name[1])  # h1 -> 1, h2 -> 2, etc.
                    
                    block = Block(
                        block_id=block_id,
                        text=text,
                        index=self.block_counter * 100,
                        block_type=BlockType.UNKNOWN,
                        style=TextStyle(bold=True)
                    )
                    block.metadata["heading_level"] = level
                    block.metadata["potential_heading"] = True
                    blocks.append(block)
            
            elif element.name == 'p':
                # Paragraph
                text = element.get_text().strip()
                if text:
                    block_id = generate_block_id(self.block_counter)
                    self.block_counter += 1
                    
                    block = Block(
                        block_id=block_id,
                        text=text,
                        index=self.block_counter * 100,
                        block_type=BlockType.UNKNOWN,
                        style=TextStyle()
                    )
                    blocks.append(block)
            
            elif element.name == 'li':
                # List item
                text = element.get_text().strip()
                if text:
                    block_id = generate_block_id(self.block_counter)
                    self.block_counter += 1
                    
                    block = Block(
                        block_id=block_id,
                        text=text,
                        index=self.block_counter * 100,
                        block_type=BlockType.UNKNOWN,
                        style=TextStyle()
                    )
                    block.metadata["is_list_item"] = True
                    blocks.append(block)
            
            elif element.name == 'img':
                # Image (placeholder - actual image data would need to be fetched)
                src = element.get('src', '')
                alt = element.get('alt', '')
                
                figure_id = generate_figure_id(self.figure_counter)
                self.figure_counter += 1
                
                figure = Figure(
                    figure_id=figure_id,
                    index=self.figure_counter,
                    caption_text=alt,
                    image_format=ImageFormat.UNKNOWN
                )
                figure.metadata["src"] = src
                figures.append(figure)
        
        return blocks, figures
