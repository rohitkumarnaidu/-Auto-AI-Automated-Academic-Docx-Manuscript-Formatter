import subprocess
import os
import platform
from typing import Optional

class PDFExporter:
    """
    Adapter for converting DOCX to PDF using LibreOffice headless.
    """
    
    def __init__(self, libreoffice_path: Optional[str] = None):
        self.libreoffice_path = libreoffice_path or self._find_libreoffice()

    def _find_libreoffice(self) -> Optional[str]:
        """Attempt to find LibreOffice executable based on OS."""
        if platform.system() == "Windows":
            paths = [
                "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe"
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
            return None # Do NOT assume on PATH if not found in common dirs
        return "libreoffice" # Linux/Mac default

    def convert_to_pdf(self, docx_path: str, output_dir: str) -> Optional[str]:
        """
        Convert DOCX to PDF using LibreOffice.
        Raises RuntimeError if LibreOffice is missing or conversion fails.
        """
        if not os.path.exists(docx_path):
            return None
            
        if not self.libreoffice_path:
            raise RuntimeError("LibreOffice not found. Please install LibreOffice to enable PDF export.")
            
        try:
            command = [
                self.libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                docx_path
            ]
            
            # Use subprocess to run conversion
            # We use shell=False for security and specific pathing
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=30,
                check=False
            )
            
            if result.returncode == 0:
                # Success. The output filename is usually the same with .pdf extension
                pdf_filename = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                
                if os.path.exists(pdf_path):
                    return pdf_path
                else:
                    raise RuntimeError(f"Conversion reported success but PDF file not found: {pdf_path}")
            
            error_msg = result.stderr or result.stdout or "Unknown LibreOffice error"
            raise RuntimeError(f"LibreOffice conversion failed: {error_msg}")
            
        except FileNotFoundError:
            raise RuntimeError(f"LibreOffice executable not found at: {self.libreoffice_path}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("PDF conversion timed out (LibreOffice hung).")
        except Exception as e:
            if isinstance(e, RuntimeError): raise e
            raise RuntimeError(f"Unexpected error during PDF conversion: {str(e)}")
