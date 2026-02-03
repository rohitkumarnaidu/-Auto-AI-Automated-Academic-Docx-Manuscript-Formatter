"""
Exporter Module - Handles saving of formatted documents.
"""

import os
from typing import Any
from app.models import Document

class Exporter:
    """
    Handles file output operations.
    """
    
    def export(self, word_doc: Any, output_path: str) -> str:
        """
        Save the Word document to disk.
        
        Args:
            word_doc: docx.Document object
            output_path: Destination path
            
        Returns:
            Absolute path to saved file
        """
        if not word_doc:
            return None
            
        # Ensure dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save
        word_doc.save(output_path)
        return output_path
