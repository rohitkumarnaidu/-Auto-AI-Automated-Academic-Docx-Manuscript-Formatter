"""
Nougat Parser — Meta AI's neural PDF parser for academic documents.

Uses facebook/nougat-base to convert scientific PDFs directly to structured
markup, with far superior extraction of equations, tables, and references
compared to traditional text-extraction tools.

Falls back gracefully if Nougat or its dependencies are unavailable.
"""

import os
import re
import logging
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Optional imports — Nougat needs torch, transformers, PIL, pypdf
# --------------------------------------------------------------------------- #
NOUGAT_AVAILABLE = False
_load_error: Optional[str] = None

try:
    import torch
    from transformers import NougatProcessor, VisionEncoderDecoderModel
    from PIL import Image
    import pypdf

    NOUGAT_AVAILABLE = True
except ImportError as exc:
    _load_error = str(exc)
    logger.info(
        "Nougat dependencies not fully installed (%s). "
        "NougatParser will be unavailable. Install with: "
        "pip install nougat-ocr torch transformers Pillow pypdf",
        exc,
    )

from app.pipeline.parsing.base_parser import BaseParser
from app.models import (
    PipelineDocument as Document,
    DocumentMetadata,
    Block,
    BlockType,
    TextStyle,
)
from app.utils.id_generator import generate_block_id

# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #
PRIMARY_MODEL = "facebook/nougat-base"
FALLBACK_MODEL = "facebook/nougat-small"  # ~350MB, for low-RAM systems
MIN_RAM_GB = 4  # Minimum free RAM to attempt loading nougat-base


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _check_available_ram_gb() -> float:
    """Return available system RAM in GB. Returns 0 on failure."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 0.0


def _pdf_to_images(file_path: str) -> List["Image.Image"]:
    """
    Convert each page of a PDF to a PIL Image using PyMuPDF (fitz).
    Falls back to pdf2image / pypdf if fitz is unavailable.
    """
    images = []

    # Try PyMuPDF first (fastest, already a dependency)
    try:
        import fitz
        pdf_doc = fitz.open(file_path)
        for page in pdf_doc:
            # Render at 200 DPI for good OCR quality
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        pdf_doc.close()
        return images
    except ImportError:
        pass

    # Fallback: use pypdf + reportlab (basic, lower quality)
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(file_path, dpi=200)
        return images
    except ImportError:
        pass

    raise RuntimeError(
        "Cannot convert PDF to images. Install PyMuPDF (pip install PyMuPDF) "
        "or pdf2image (pip install pdf2image)."
    )


def _classify_nougat_line(line: str) -> BlockType:
    """
    Heuristic classification of a Nougat output line into a BlockType.
    Nougat outputs LaTeX-like / Markdown-like markup.
    """
    stripped = line.strip()
    if not stripped:
        return BlockType.UNKNOWN

    # Section headings: map markdown depth to HEADING_1..HEADING_3
    if stripped.startswith("### "):
        return BlockType.HEADING_3
    if stripped.startswith("## "):
        return BlockType.HEADING_2
    if stripped.startswith("# "):
        return BlockType.HEADING_1

    # Abstract
    if stripped.lower().startswith("abstract"):
        return BlockType.ABSTRACT

    # References section
    if stripped.lower() in ("references", "bibliography"):
        return BlockType.HEADING_1

    # Equations (LaTeX delimiters)
    if stripped.startswith("\\[") or stripped.startswith("$$"):
        return BlockType.UNKNOWN  # equation — no dedicated BlockType

    # List items
    if stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s", stripped):
        return BlockType.LIST_ITEM

    # Table markers
    if "|" in stripped and stripped.count("|") >= 2:
        return BlockType.UNKNOWN  # table row

    return BlockType.BODY


# --------------------------------------------------------------------------- #
#  Main class
# --------------------------------------------------------------------------- #
class NougatParser(BaseParser):
    """
    Parses academic PDF files using Meta's Nougat model.

    Nougat converts each PDF page image into structured Markdown/LaTeX text,
    providing superior extraction of equations, tables, and references.

    Model loading:
      1. Try facebook/nougat-base  (~1GB, best quality)
      2. Fall back to facebook/nougat-small  (~350MB, less RAM)
      3. If both fail, __init__ raises ImportError (factory skips us)
    """

    def __init__(self):
        if not NOUGAT_AVAILABLE:
            raise ImportError(
                f"Nougat dependencies unavailable: {_load_error}. "
                "Install with: pip install nougat-ocr torch transformers Pillow pypdf"
            )

        self.model = None
        self.processor = None
        self.device = None
        self.active_model_name: str = ""
        self.block_counter = 0

        # Lazy-load: model is loaded on first parse() call, not at import time
        self._model_loaded = False

    def _ensure_model_loaded(self):
        """Lazy-load the Nougat model on first use."""
        if self._model_loaded:
            return

        from app.services.model_store import model_store

        # Check ModelStore cache first
        if model_store.is_loaded("nougat_model") and model_store.is_loaded("nougat_processor"):
            self.model = model_store.get_model("nougat_model")
            self.processor = model_store.get_model("nougat_processor")
            self.device = next(self.model.parameters()).device
            self.active_model_name = "cached"
            self._model_loaded = True
            print("NougatParser: Reusing cached model from ModelStore.")
            return

        # Detect device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("NougatParser: Using device: %s", self.device)

        # Choose model based on available RAM
        available_ram = _check_available_ram_gb()
        model_name = PRIMARY_MODEL if available_ram >= MIN_RAM_GB else FALLBACK_MODEL

        # Try primary, then fallback
        for name in [model_name, FALLBACK_MODEL]:
            try:
                print(f"NougatParser: Loading model '{name}'... (this may download ~1GB on first use)")
                self.processor = NougatProcessor.from_pretrained(name)
                self.model = VisionEncoderDecoderModel.from_pretrained(name)
                self.model.to(self.device)
                self.model.eval()
                self.active_model_name = name

                # Cache in ModelStore
                model_store.set_model("nougat_model", self.model)
                model_store.set_model("nougat_processor", self.processor)

                print(f"NougatParser: ✅ Model '{name}' loaded on {self.device}.")
                self._model_loaded = True
                return
            except Exception as exc:
                logger.warning("NougatParser: Failed to load '%s': %s", name, exc)
                if name == FALLBACK_MODEL:
                    raise RuntimeError(
                        f"NougatParser: Could not load any Nougat model. Last error: {exc}"
                    )

    def supports_format(self, file_extension: str) -> bool:
        """Nougat supports PDF files only."""
        return file_extension.lower() == ".pdf"

    def parse(self, file_path: str, document_id: str) -> Document:
        """
        Parse a PDF file using Nougat into a Document model.

        Args:
            file_path: Path to the .pdf file
            document_id: Unique identifier for this document

        Returns:
            Document instance with all extracted content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        # Load model on first call
        self._ensure_model_loaded()

        # Reset counter
        self.block_counter = 0

        if not isinstance(document_id, str):
            document_id = str(document_id)

        # Initialize document
        document = Document(
            document_id=document_id,
            original_filename=Path(file_path).name,
            source_path=file_path,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        document.metadata = DocumentMetadata()

        # Convert PDF pages to images
        print(f"NougatParser: Converting PDF to images...")
        page_images = _pdf_to_images(file_path)
        print(f"NougatParser: Processing {len(page_images)} pages with Nougat...")

        # Run inference on each page
        all_text_parts: List[str] = []
        for page_num, img in enumerate(page_images):
            try:
                page_text = self._process_page(img)
                if page_text:
                    all_text_parts.append(page_text)
            except Exception as exc:
                logger.warning(
                    "NougatParser: Failed to process page %d: %s", page_num + 1, exc
                )

        # Parse the combined Nougat output into blocks
        full_text = "\n\n".join(all_text_parts)
        blocks = self._parse_nougat_output(full_text)

        document.blocks = blocks
        document.figures = []  # Nougat doesn't extract images separately

        document.add_processing_stage(
            stage_name="parsing",
            status="success",
            message=(
                f"Parsed PDF with Nougat ({self.active_model_name}): "
                f"{len(blocks)} blocks from {len(page_images)} pages"
            ),
        )

        document.metadata.ai_hints = document.metadata.ai_hints or {}
        document.metadata.ai_hints["parser"] = "nougat"
        document.metadata.ai_hints["nougat_model"] = self.active_model_name

        print(f"NougatParser: ✅ Extracted {len(blocks)} blocks from {len(page_images)} pages.")
        return document

    # ------------------------------------------------------------------ #
    #  Internal
    # ------------------------------------------------------------------ #
    def _process_page(self, image: "Image.Image") -> str:
        """Run Nougat inference on a single page image."""
        # Prepare input
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        # Generate output tokens
        with torch.no_grad():
            outputs = self.model.generate(
                pixel_values,
                min_length=1,
                max_new_tokens=4096,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            )

        # Decode
        page_text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]

        # Post-process: remove repetition artifacts (common in Nougat output)
        page_text = self.processor.post_process_generation(
            page_text, fix_markdown=True
        )

        return page_text

    def _parse_nougat_output(self, text: str) -> List[Block]:
        """Convert raw Nougat Markdown/LaTeX output into Block objects."""
        blocks: List[Block] = []
        if not text:
            return blocks

        # Split into logical blocks by double newlines
        raw_blocks = re.split(r"\n{2,}", text)

        for raw in raw_blocks:
            raw = raw.strip()
            if not raw:
                continue

            block_type = _classify_nougat_line(raw)

            # Clean up heading markers for the block text
            clean_text = raw
            heading_level = 0
            if raw.startswith("### "):
                clean_text = raw[4:]
                heading_level = 3
            elif raw.startswith("## "):
                clean_text = raw[3:]
                heading_level = 2
            elif raw.startswith("# "):
                clean_text = raw[2:]
                heading_level = 1

            block_id = generate_block_id(self.block_counter)
            self.block_counter += 1

            style = TextStyle(bold=(heading_level > 0))

            block = Block(
                block_id=block_id,
                text=clean_text,
                index=self.block_counter * 100,
                block_type=block_type,
                style=style,
            )

            if heading_level > 0:
                block.metadata["heading_level"] = heading_level
                block.metadata["potential_heading"] = True

            # Flag equations
            if "\\[" in raw or "$$" in raw or "\\begin{" in raw:
                block.metadata["has_equation"] = True

            # Flag tables
            if "|" in raw and raw.count("|") >= 2:
                block.metadata["is_table"] = True

            block.metadata["parser"] = "nougat"
            blocks.append(block)

        return blocks
