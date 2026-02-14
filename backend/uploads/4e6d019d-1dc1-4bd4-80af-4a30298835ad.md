# Sample Inputs Directory

## Purpose

This directory should contain test DOCX files for manual testing.

## Required Files

Please add the following test files:

### 1. simple.docx
**Content**: Basic academic paper
- Title
- Author(s)
- Abstract
- Introduction
- Methods
- Results
- Conclusion
- References

**Purpose**: Test basic parsing and classification

---

### 2. with_figures.docx
**Content**: Document with images
- All content from simple.docx
- 2-3 figures with captions
- Figure references in text (e.g., "as shown in Figure 1")

**Purpose**: Test figure detection and caption matching

---

### 3. with_tables.docx
**Content**: Document with tables
- All content from simple.docx
- 2-3 tables with captions
- Table references in text (e.g., "see Table 1")

**Purpose**: Test table extraction and caption matching

---

### 4. with_equations.docx
**Content**: Document with mathematical equations
- All content from simple.docx
- Inline equations (e.g., x²)
- Display equations (e.g., E=mc²)

**Purpose**: Test equation extraction and MathML conversion

---

## How to Add Files

1. Copy existing DOCX files from `backend/uploads/` directory
2. Rename them to match the naming convention above
3. Place them in this directory

Example:
```bash
# From backend directory
cp uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx manual_tests/sample_inputs/simple.docx
```

---

## Alternative: Use Existing Uploads

If you don't have specific test files, you can run tests directly on files in `uploads/`:

```bash
# Example using existing upload
python manual_tests/phase1_identification/run_input_conversion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
