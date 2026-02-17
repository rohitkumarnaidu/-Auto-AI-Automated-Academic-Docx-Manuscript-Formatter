"""
Figure analysis tool for detecting and analyzing figures in documents.
"""
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.pipeline.services.docling_client import DoclingClient


class FigureToolInput(BaseModel):
    """Input schema for figure analysis tool."""
    file_path: str = Field(description="Path to the document file to analyze figures")


class FigureAnalysisTool(BaseTool):
    """
    Tool for detecting and analyzing figures in academic documents.
    
    This tool uses Docling to identify figures, extract captions,
    and analyze their placement within the document.
    """
    name: str = "analyze_figures"
    description: str = (
        "Detect and analyze figures in a document. "
        "Returns information about figure count, captions, positions, and quality. "
        "Use this when you need to understand the visual content and "
        "ensure proper figure formatting."
    )
    args_schema: Type[BaseModel] = FigureToolInput
    
    def __init__(self):
        super().__init__()
        self.docling_client = DoclingClient()
    
    def _run(self, file_path: str) -> str:
        """
        Execute figure analysis.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            JSON string containing figure analysis results
        """
        try:
            # Analyze layout to find figures
            layout_data = self.docling_client.analyze_layout(file_path)
            
            if not layout_data:
                return "ERROR: Failed to analyze document for figures."
            
            blocks = layout_data.get("blocks", [])
            
            # Extract figure information
            figures = []
            for block in blocks:
                if block.get("block_type") == "figure":
                    figure_info = {
                        "caption": block.get("text", "No caption"),
                        "position": block.get("bbox", {}),
                        "page": block.get("page", 0),
                        "has_caption": bool(block.get("text"))
                    }
                    figures.append(figure_info)
            
            # Analyze figure quality
            quality_issues = []
            for idx, fig in enumerate(figures, 1):
                if not fig["has_caption"]:
                    quality_issues.append(f"Figure {idx} missing caption")
                if not fig["position"]:
                    quality_issues.append(f"Figure {idx} position unclear")
            
            # Format response
            result = {
                "status": "success",
                "figures": {
                    "total_count": len(figures),
                    "with_captions": sum(1 for f in figures if f["has_caption"]),
                    "quality_issues": quality_issues,
                    "figures": figures[:10]  # First 10 figures
                }
            }
            
            import json
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"ERROR: Figure analysis failed: {str(e)}"
    
    async def _arun(self, file_path: str) -> str:
        """Async version - not implemented yet."""
        raise NotImplementedError("Async execution not supported yet")
