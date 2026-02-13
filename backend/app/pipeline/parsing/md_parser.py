"""
Markdown Parser - Extract content from Markdown (.md) files.

Parses Markdown syntax to extract:
- Headings (# ## ###)
- Paragraphs
- Lists
- Code blocks
- Images
- Links
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
    Figure,
    ImageFormat,
)
from app.utils.id_generator import generate_block_id, generate_figure_id


class MarkdownParser(BaseParser):
    """Parses Markdown (.md) files into Document model instances."""
    
    def __init__(self):
        """Initialize the Markdown parser."""
        self.block_counter = 0
        self.figure_counter = 0
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if this parser supports Markdown format."""
        return file_extension.lower() in ['.md', '.markdown']
    
    def parse(self, file_path: str, document_id: str) -> Document:
        """
        Parse a Markdown file into a Document model.
        
        Args:
            file_path: Path to the .md file
            document_id: Unique identifier for this document
        
        Returns:
            Document instance with all extracted content
        
        Raises:
            FileNotFoundError: If Markdown file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        # Reset counters
        self.block_counter = 0
        self.figure_counter = 0
        
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
        
        # Extract metadata (from YAML frontmatter if present)
        content, metadata = self._extract_frontmatter(content)
        document.metadata = metadata
        
        # Extract content
        blocks, figures = self._extract_content(content)
        
        document.blocks = blocks
        document.figures = figures
        
        # Add processing history
        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=f"Parsed Markdown: {len(blocks)} blocks, {len(figures)} figures"
        )
        
        return document
    
    def _extract_frontmatter(self, content: str) -> tuple:
        """Extract YAML frontmatter if present."""
        metadata = DocumentMetadata()
        
        # Check for YAML frontmatter (--- ... ---)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter = match.group(1)
            content = content[match.end():]
            
            # Simple YAML parsing (basic key: value)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'title':
                        metadata.title = value
                    elif key == 'author':
                        metadata.authors = [value]
                    elif key == 'keywords':
                        metadata.keywords = [k.strip() for k in value.split(',')]
        
        return content, metadata
    
    def _extract_content(self, content: str) -> tuple:
        """Extract blocks and figures from Markdown content."""
        blocks = []
        figures = []
        
        lines = content.split('\n')
        i = 0
        current_paragraph = []
        
        while i < len(lines):
            line = lines[i]
            
            # Heading
            if line.startswith('#'):
                # Save previous paragraph
                if current_paragraph:
                    blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
                
                # Create heading block
                heading_text = line.lstrip('#').strip()
                level = len(line) - len(line.lstrip('#'))
                
                block_id = generate_block_id(self.block_counter)
                self.block_counter += 1
                
                block = Block(
                    block_id=block_id,
                    text=heading_text,
                    index=self.block_counter * 100,
                    block_type=BlockType.UNKNOWN,
                    style=TextStyle(bold=True)
                )
                block.metadata["heading_level"] = level
                block.metadata["potential_heading"] = True
                blocks.append(block)
            
            # Image ![alt](url)
            elif '![' in line:
                # Save previous paragraph
                if current_paragraph:
                    blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
                
                # Extract image
                img_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
                for match in re.finditer(img_pattern, line):
                    alt_text = match.group(1)
                    url = match.group(2)
                    
                    figure_id = generate_figure_id(self.figure_counter)
                    self.figure_counter += 1
                    
                    figure = Figure(
                        figure_id=figure_id,
                        index=self.figure_counter,
                        caption_text=alt_text,
                        image_format=ImageFormat.UNKNOWN
                    )
                    figure.metadata["src"] = url
                    figures.append(figure)
            
            # Empty line (paragraph break)
            elif line.strip() == '':
                if current_paragraph:
                    blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
            
            # Regular text
            else:
                current_paragraph.append(line)
            
            i += 1
        
        # Save final paragraph
        if current_paragraph:
            blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
        
        return blocks, figures
    
    def _create_paragraph_block(self, text: str) -> Block:
        """Create a paragraph block from text."""
        block_id = generate_block_id(self.block_counter)
        self.block_counter += 1
        
        # Detect list items
        is_list = text.strip().startswith(('-', '*', '+')) or re.match(r'^\d+\.', text.strip())
        
        block = Block(
            block_id=block_id,
            text=text.strip(),
            index=self.block_counter * 100,
            block_type=BlockType.UNKNOWN,
            style=TextStyle()
        )
        
        if is_list:
            block.metadata["is_list_item"] = True
        
        return block
