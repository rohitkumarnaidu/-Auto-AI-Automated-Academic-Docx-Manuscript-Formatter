# DOCX Visual Testing Framework

## Purpose

This framework provides **DOCX-in, DOCX-out** manual testing for visual inspection of the ScholarForm AI pipeline. Each test outputs an annotated DOCX file that you open in Microsoft Word to verify correctness.

**Goal**: Detect duplication, heading issues, caption problems, and reference repetition through visual inspection.

---

## Directory Structure

```
manual_tests/
├── visual/
│   ├── 01_parse_and_structure.py
│   ├── 02_classification.py
│   ├── 03_figures_tables.py
│   ├── 04_references.py
│   ├── 05_full_pipeline.py
│   └── 06_formatted.py
├── visual_outputs/
│   └── (generated annotated DOCX files)
└── README_VISUAL.md (this file)
```

---

## Testing Workflow

### Stage 1: Parse and Structure Detection

**Command**:
```bash
python manual_tests/visual/01_parse_and_structure.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

**Output**: `manual_tests/visual_outputs/01_structure_annotated.docx`

**What to check**:
- Yellow highlights = Detected headings
- Blue annotations = Heading levels
- Red text = Duplicate blocks
- Summary at top shows total blocks, headings, duplicates

**⚠️ STOP** - Open output in Word, inspect, report findings

---

### Stage 2: Semantic Classification

**Command**:
```bash
python manual_tests/visual/02_classification.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

**Output**: `manual_tests/visual_outputs/02_classified_annotated.docx`

**What to check**:
- Green annotations = High confidence sections
- Blue annotations = Medium confidence
- Orange annotations = Low confidence (review needed)
- Verify Abstract, Introduction, Methods, etc. are correctly labeled

**⚠️ STOP** - Open output in Word, inspect, report findings

---

### Stage 3: Figure and Table Detection

**Command**:
```bash
python manual_tests/visual/03_figures_tables.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

**Output**: `manual_tests/visual_outputs/03_figures_tables_annotated.docx`

**What to check**:
- Cyan annotations = Figure captions
- Magenta annotations = Table captions
- Verify all figures/tables detected
- Check for duplicates

**⚠️ STOP** - Open output in Word, inspect, report findings

---

### Stage 4: Reference Extraction

**Command**:
```bash
python manual_tests/visual/04_references.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

**Output**: `manual_tests/visual_outputs/04_references_annotated.docx`

**What to check**:
- Purple annotations = Detected references
- Verify all references extracted
- Check for duplicate references

**⚠️ STOP** - Open output in Word, inspect, report findings

---

### Stage 5: Full Pipeline (No Formatting)

**Command**:
```bash
python manual_tests/visual/05_full_pipeline.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx
```

**Output**: `manual_tests/visual_outputs/05_full_pipeline_annotated.docx`

**What to check**:
- All previous annotations combined
- Comprehensive duplication report at top
- Red "DUPLICATE" annotations for any duplicated content
- Summary shows if ready for formatting

**⚠️ CRITICAL**: If duplicates found, DO NOT proceed to Stage 6

**⚠️ STOP** - Open output in Word, inspect, report findings

---

### Stage 6: Final Formatted Output

**Command**:
```bash
python manual_tests/visual/06_formatted.py uploads/132dbdae-b6e3-4936-bdb5-bc398ed0ac19.docx --template IEEE
```

**Output**: `manual_tests/visual_outputs/06_final_IEEE.docx`

**What to check**:
1. **Duplication**:
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

**⚠️ STOP** - Open output in Word, perform full quality check

---

## Decision Tree

```
Stage N has duplicates or errors?
├─ YES → Fix pipeline logic, re-run from Stage 1
└─ NO → Proceed to Stage N+1

Stage 5 has duplicates?
├─ YES → DO NOT proceed to Stage 6, fix pipeline first
└─ NO → Proceed to Stage 6 (formatting)

Stage 6 has formatting issues (but NO duplicates)?
├─ YES → Fix formatter ONLY, re-run Stage 6
└─ NO → Done ✅
```

---

## Key Principles

✅ **DOCX input only** - No JSON files  
✅ **DOCX output only** - Visual inspection in Word  
✅ **Cumulative stages** - Each stage includes previous stages  
✅ **Stop after each stage** - Report findings before proceeding  
✅ **Fix at correct layer** - Duplication = pipeline, Formatting = formatter  

❌ **Do NOT** skip stages  
❌ **Do NOT** proceed if duplicates found  
❌ **Do NOT** modify pipeline logic without re-running from Stage 1  

---

## Next Steps

1. **Run Stage 1** with your test DOCX
2. **Open output** in Microsoft Word
3. **Inspect visually** for headings and duplicates
4. **Report findings** before proceeding to Stage 2
