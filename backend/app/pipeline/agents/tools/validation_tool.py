"""
Validation tool using AI-based analysis.
"""
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.pipeline.validation.validator import DocumentValidator
from app.models import PipelineDocument


class ValidationToolInput(BaseModel):
    """Input schema for validation tool."""
    document_id: str = Field(description="ID of the document to validate")


class ValidationTool(BaseTool):
    """
    Tool for validating document structure and metadata.
    
    This tool wraps the DocumentValidator to check document quality,
    completeness, and academic formatting compliance.
    """
    name: str = "validate_document"
    description: str = (
        "Validate the structure, metadata, and formatting of a document. "
        "Returns validation results including errors, warnings, and confidence scores. "
        "Use this to ensure the document meets academic standards and is properly formatted."
    )
    args_schema: Type[BaseModel] = ValidationToolInput
    
    def __init__(self):
        super().__init__()
        self.validator = DocumentValidator()
        self._document_cache = {}  # Simple cache for demo purposes
    
    def set_document(self, doc_id: str, document: PipelineDocument):
        """Cache a document for validation."""
        self._document_cache[doc_id] = document
    
    def _run(self, document_id: str) -> str:
        """
        Execute document validation.
        
        Args:
            document_id: ID of the document to validate
            
        Returns:
            JSON string containing validation results
        """
        try:
            # Retrieve document from cache
            document = self._document_cache.get(document_id)
            
            if not document:
                return f"ERROR: Document with ID '{document_id}' not found in cache."
            
            # Validate document
            validated_doc = self.validator.validate(document)
            
            # Format response
            result = {
                "status": "success",
                "validation": {
                    "is_valid": validated_doc.is_valid,
                    "error_count": len(validated_doc.validation_errors),
                    "warning_count": len(validated_doc.validation_warnings),
                    "errors": validated_doc.validation_errors[:5],  # First 5 errors
                    "warnings": validated_doc.validation_warnings[:5],  # First 5 warnings
                    "metadata_quality": {
                        "has_title": bool(validated_doc.metadata.title),
                        "has_authors": len(validated_doc.metadata.authors) > 0,
                        "has_abstract": bool(validated_doc.metadata.abstract),
                        "reference_count": len(validated_doc.references)
                    }
                }
            }
            
            import json
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"ERROR: Validation failed: {str(e)}"
    
    async def _arun(self, document_id: str) -> str:
        """Async version - not implemented yet."""
        raise NotImplementedError("Async execution not supported yet")
