# Complete Manual Testing Guide

## All Available Scripts

### Phase 1: Identification Verification (11 scripts)

1. ✅ `run_input_conversion.py` - DOCX → Block extraction
2. ✅ `run_structure.py` - Heading detection
3. ✅ `run_classifier.py` - Semantic classification
4. ✅ `run_figure_detection.py` - Figure extraction
5. ✅ `run_caption_matching.py` - Figure-caption association
6. ✅ `run_figure_numbering.py` - Figure numbering
7. ✅ `run_figure_insertion.py` - Figure insertion points
8. ✅ `run_table_extraction.py` - Table extraction
9. ✅ `run_table_caption_matching.py` - Table-caption association
10. ✅ `run_table_numbering.py` - Table numbering
11. ✅ `run_table_insertion.py` - Table insertion points

### Phase 2: Assembly & Deduplication (2 scripts)

12. ✅ `run_validation.py` - Duplication check
13. ✅ `run_pipeline.py` - Full pipeline (no formatting)

### Phase 3: Formatting (1 script)

14. ✅ `run_formatter.py` - Final DOCX formatting

---

## Complete Testing Workflow

### PHASE 1: IDENTIFICATION VERIFICATION

**Goal**: Confirm the system IDENTIFIES content correctly before formatting

#### Step 1: Input Conversion
```bash
python manual_tests/phase1_identification/run_input_conversion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/01_blocks.json` - All blocks extracted, no duplicates

#### Step 2: Structure Detection
```bash
python manual_tests/phase1_identification/run_structure.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/02_structure.json` - Headings detected, levels assigned

#### Step 3: Semantic Classification
```bash
python manual_tests/phase1_identification/run_classifier.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/03_classified.json` - Abstract, Introduction, Methods identified

#### Step 4: Figure Detection
```bash
python manual_tests/phase1_identification/run_figure_detection.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/04_figures.json` - All figures extracted, unique IDs

#### Step 5: Figure Caption Matching
```bash
python manual_tests/phase1_identification/run_caption_matching.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/05_figures_with_captions.json` - Captions matched to figures

#### Step 5b: Figure Numbering
```bash
python manual_tests/phase1_identification/run_figure_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/05b_figures_numbered.json` - Sequential numbering (1, 2, 3...)

#### Step 5c: Figure Insertion
```bash
python manual_tests/phase1_identification/run_figure_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/05c_figures_insertion.json` - Correct insertion points

#### Step 6: Table Extraction
```bash
python manual_tests/phase1_identification/run_table_extraction.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/06_tables.json` - All tables extracted, unique IDs

#### Step 7: Table Caption Matching
```bash
python manual_tests/phase1_identification/run_table_caption_matching.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/07_tables_with_captions.json` - Captions matched to tables

#### Step 7b: Table Numbering
```bash
python manual_tests/phase1_identification/run_table_numbering.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/06b_tables_numbered.json` - Sequential numbering (1, 2, 3...)

#### Step 7c: Table Insertion
```bash
python manual_tests/phase1_identification/run_table_insertion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/06c_tables_insertion.json` - Correct insertion points

**⚠️ STOP** - Review all Phase 1 outputs before proceeding

---

### PHASE 2: STRUCTURE & DEDUPLICATION CHECK

**Goal**: Ensure no duplication, single source of truth for all content

#### Step 8: Validation
```bash
python manual_tests/phase2_assembly/run_validation.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/08_validation_report.json`
- `has_any_duplicates`: should be `false`
- `unique_blocks` should equal `total_blocks`
- `unique_figures` should equal `total_figures`
- `unique_tables` should equal `total_tables`

#### Step 9: Full Pipeline (No Formatting)
```bash
python manual_tests/phase2_assembly/run_pipeline.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```
**Check**: `outputs/09_pipeline_document.json`
- All content identified
- No crashes
- Processing history shows no errors

**⚠️ CRITICAL DECISION POINT**:
- If duplicates found → Fix pipeline logic, re-run from Step 1
- If no duplicates → Proceed to Phase 3

---

### PHASE 3: FORMATTING

**Goal**: Apply formatting and verify final DOCX quality

#### Step 10: Formatter
```bash
python manual_tests/phase3_formatting/run_formatter.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx --template IEEE
```
**Output**: `outputs/10_formatted_ieee.docx`

**Manual Inspection in Microsoft Word**:
1. **Duplication Check**:
   - Are headings duplicated?
   - Are figures appearing twice?
   - Are tables duplicated?
   - Are references repeated?

2. **Heading Hierarchy**:
   - H1 > H2 > H3 visual distinction
   - Consistent spacing
   - Proper nesting

3. **Caption Placement**:
   - Figures: caption BELOW image
   - Tables: caption ABOVE table

4. **Reference Formatting**:
   - Consistent style
   - No duplicates
   - Proper numbering

5. **Completeness**:
   - No missing sections
   - All content from original present

---

## Decision Tree

```
Phase 1 has issues?
├─ YES → Fix identification logic, re-run from Step 1
└─ NO → Proceed to Phase 2

Phase 2 has duplicates?
├─ YES → Fix pipeline logic, re-run from Step 1
└─ NO → Proceed to Phase 3

Phase 3 has formatting issues (but NO duplicates)?
├─ YES → Fix formatter ONLY, re-run Step 10
└─ NO → Done ✅
```

---

## Key Principles

✅ **Stop after each phase** - Report findings  
✅ **Fix at correct layer** - Identification vs Formatting  
✅ **No formatting fixes until Phase 1+2 pass**  
✅ **Manual verification required** - Open JSON/DOCX files  

❌ **Do NOT skip phases**  
❌ **Do NOT redesign pipeline**  
❌ **Do NOT auto-fix without verification**  

---

## Next Steps

**START HERE**:
```bash
python manual_tests/phase1_identification/run_input_conversion.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

Open `manual_tests/outputs/01_blocks.json` and report findings.
