import subprocess
import os
import platform
from typing import Optional
from app.config.settings import settings  # Import settings for dynamic path

class PDFExporter:
    """
    Adapter for converting DOCX to PDF using LibreOffice headless.
    """
    
    def __init__(self, libreoffice_path: Optional[str] = None):
        self.libreoffice_path = libreoffice_path or settings.LIBREOFFICE_PATH or self._find_libreoffice()

    def _find_libreoffice(self) -> Optional[str]:
        """Attempt to find LibreOffice executable based on OS (dynamic cross-platform)."""
        if platform.system() == "Windows":
            paths = [
                "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe"
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
            return None  # Do NOT assume on PATH if not found in common dirs
        elif platform.system() == "Darwin":  # macOS
            return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        else:  # Linux
            return "libreoffice"  # Usually on PATH

    def convert_to_pdf(self, docx_path: str, output_dir: str) -> Optional[str]:
        """
        Convert DOCX to PDF using LibreOffice, falling back to docx2pdf.
        Raises RuntimeError if both engines fail.
        """
        if not os.path.exists(docx_path):
            return None
            
        import logging
        logger = logging.getLogger(__name__)
        pdf_filename = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # 1. Try LibreOffice
        if self.libreoffice_path:
            try:
                command = [
                    self.libreoffice_path,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", output_dir,
                    docx_path
                ]
                
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    check=False
                )
                
                if result.returncode == 0 and os.path.exists(pdf_path):
                    return pdf_path
                
                error_msg = result.stderr or result.stdout or "Unknown LibreOffice error"
                raise RuntimeError(f"LibreOffice conversion failed: {error_msg}")
                
            except Exception as lo_err:
                logger.warning("LibreOffice conversion failed: %s. Trying docx2pdf fallback...", lo_err)
        else:
            logger.warning("LibreOffice not found. Trying docx2pdf fallback directly...")
            
        # 2. Try docx2pdf Fallback
        try:
            from docx2pdf import convert
            # docx2pdf requires an absolute path on Windows, let's make sure
            convert(os.path.abspath(docx_path), os.path.abspath(pdf_path))
            if os.path.exists(pdf_path):
                return pdf_path
            raise RuntimeError(f"generated PDF not found at: {pdf_path}")
        except Exception as d2p_err:
            logger.error("docx2pdf also failed: %s", d2p_err)
            raise RuntimeError(f"Both PDF export engines failed. Final error: {d2p_err}")
