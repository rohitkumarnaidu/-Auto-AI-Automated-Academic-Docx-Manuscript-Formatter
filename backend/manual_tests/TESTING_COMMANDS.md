# 🧪 Complete Manual Testing Commands

This guide lists **ALL commands** for every step of the manual testing process, organized by phase and type.

## 📂 Manual Test Directory Structure

```
manual_tests/
├── phase1_identification/      # JSON outputs (Detailed Data)
│   ├── run_input_conversion.py
│   ├── run_structure.py
│   ├── run_classifier.py
│   ├── run_figure_detection.py
│   ├── run_caption_matching.py
│   ├── run_figure_numbering.py
│   ├── run_figure_insertion.py
│   ├── run_table_extraction.py
│   ├── run_table_caption_matching.py
│   ├── run_table_numbering.py
│   └── run_table_insertion.py
│
├── phase2_assembly/            # JSON outputs (Validation)
│   ├── run_validation.py
│   └── run_pipeline.py
│
├── phase3_formatting/          # DOCX outputs (Final)
│   └── run_formatter.py
│
├── visual/                     # DOCX outputs (Visual Inspection)
│   ├── phase1/                 # Visual Indentification
│   │   ├── 01_parse_and_structure.py
│   │   ├── 02_classification.py
│   │   ├── 03_figures_tables.py
│   │   ├── 04_references.py
│   │   ├── 05b_figure_numbering.py
│   │   ├── 05c_figure_insertion.py
│   │   ├── 06b_table_numbering.py
│   │   └── 06c_table_insertion.py
│   ├── phase2/                 # Visual Assembly
│   │   └── 05_full_pipeline.py
│   └── phase3/                 # Visual Formatting
│       └── 06_formatted.py
│
├── outputs/                    # JSON Test Results
└── visual_outputs/             # DOCX Test Results
```

---

## 🎯 PHASE 1: IDENTIFICATION VERIFICATION

### Step 1: Input Conversion & Parsing
**Goal**: Verify DOCX parsing and initial block extraction.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_input_conversion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/01_blocks.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/01_parse_and_structure.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/01_structure_annotated.docx`)*

---

### Step 2: Structure Detection
**Goal**: Verify headings and document hierarchy.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_structure.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/02_structure.json`)*

- **Visual (DOCX Output)**:
  *(Same as Step 1 - Structure is included in `01_structure_annotated.docx`)*

---

### Step 3: Semantic Classification
**Goal**: Verify section types (Abstract, Introduction, Methods, etc.).

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_classifier.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/03_classified.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/02_classification.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/02_classified_annotated.docx`)*

---

### Step 4: Figure Detection
**Goal**: Verify extraction of images and figure blocks.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_figure_detection.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/04_figures.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/03_figures_tables.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/03_figures_tables_annotated.docx`)*

---

### Step 5: Figure Caption Matching
**Goal**: Verify captions are correctly linked to figures.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_caption_matching.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/05_figures_with_captions.json`)*

- **Visual (DOCX Output)**:
  *(Included in Step 4 - Captions are highlighted in Cyan in `03_figures_tables_annotated.docx`)*

---

### Step 5b: Figure Numbering
**Goal**: Verify sequential numbering (Figure 1, Figure 2...).

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_figure_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/05b_figures_numbered.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/05b_figure_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/05b_figure_numbering_annotated.docx`)*

---

### Step 5c: Figure Insertion Points
**Goal**: Verify correct placement anchor locations.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_figure_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/05c_figures_insertion.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/05c_figure_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/05c_figure_insertion_annotated.docx`)*

---

### Step 6: Table Extraction
**Goal**: Verify table content extraction.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_table_extraction.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/06_tables.json`)*

- **Visual (DOCX Output)**:
  *(Included in Step 4 - Tables are highlighted in `03_figures_tables_annotated.docx`)*

---

### Step 7: Table Caption Matching
**Goal**: Verify captions are linked to tables.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_table_caption_matching.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/07_tables_with_captions.json`)*

- **Visual (DOCX Output)**:
  *(Included in Step 4 - Captions highlighted in Magenta in `03_figures_tables_annotated.docx`)*

---

### Step 7b: Table Numbering
**Goal**: Verify sequential numbering (Table I, Table II...).

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_table_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/06b_tables_numbered.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/06b_table_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/06b_table_numbering_annotated.docx`)*

---

### Step 7c: Table Insertion Points
**Goal**: Verify correct table anchor locations.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase1/run_table_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/06c_tables_insertion.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/06c_table_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/06c_table_insertion_annotated.docx`)*

---

### Step 8: Reference Extraction
**Goal**: Verify bibliography parsing.

- **Normal (JSON Output)**:
  *(No separate script for this yet - part of main pipeline)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase1/04_references.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/04_references_annotated.docx`)*

---

## 🎯 PHASE 2: ASSEMBLY & DEDUPLICATION

### Step 9: Validation Check
**Goal**: Ensure NO duplicates exist before assembly.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase2/run_validation.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/08_validation_report.json`)*

### Step 10: Full Pipeline Assembly
**Goal**: Verify complete document structure without formatting.

- **Normal (JSON Output)**:
  ```bash
  python manual_tests/normal/phase2/run_pipeline.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/outputs/09_pipeline_document.json`)*

- **Visual (DOCX Output)**:
  ```bash
  python manual_tests/visual/phase2/05_full_pipeline.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
  ```
  *(Output: `manual_tests/visual_outputs/05_full_pipeline_annotated.docx` - Check specifically for RED duplicate warnings)*

---

## 🎯 PHASE 3: FORMATTING

### Step 11: Final Output Generation
**Goal**: Generate the final publication-ready DOCX.

- **Normal (Produces Final DOCX)**:
  ```bash
  python manual_tests/normal/phase3/run_formatter.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx --template IEEE
  ```
  *(Output: `manual_tests/outputs/10_formatted_ieee.docx`)*

- **Visual Test (Annotated Final Check)**:
  ```bash
  python manual_tests/visual/phase3/06_formatted.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx --template IEEE
  ```
  *(Output: `manual_tests/visual_outputs/06_final_IEEE.docx`)*
