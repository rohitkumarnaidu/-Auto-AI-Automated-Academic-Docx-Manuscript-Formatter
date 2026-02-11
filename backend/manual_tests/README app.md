# Manual Test Scripts

This directory contains **manual verification scripts** for quality assurance of the ScholarForm AI formatting pipeline.

## Purpose

These scripts are **NOT production code**. They are manual testing utilities to verify:
- Backend processing logic
- Data structure contracts
- AI/RAG output consistency
- Equation conversion quality

## Directory Structure

```
app/manual_tests/
├── equations/
│   └── verify_equations.py          # OMML → MathML conversion check
├── hitl/
│   └── verify_hitl_jats.py          # HITL signals + JATS XML validation
├── interface/
│   └── verify_interface.py          # Backend output contract check
├── rag/
│   └── verify_rag_interface.py      # RAG/AI output format validation
├── audit/
│   └── verify_audit_fixes.py        # Post-audit maintenance verification
└── README.md                         # This file
```

## Usage

### Run Individual Tests

```bash
# From backend/ directory
python app/manual_tests/equations/verify_equations.py
python app/manual_tests/hitl/verify_hitl_jats.py
python app/manual_tests/interface/verify_interface.py
python app/manual_tests/rag/verify_rag_interface.py
python app/manual_tests/audit/verify_audit_fixes.py
```

### Run All Tests

```bash
# Create a test runner (optional)
python -m pytest app/manual_tests/ -v
```

## Important Notes

1. **These are NOT unit tests** - They verify end-to-end pipeline behavior
2. **Manual review still required** - Scripts check backend logic, not visual formatting
3. **Run before QA** - Use these to confirm backend processing succeeded before manual DOCX review
4. **Not in CI/CD** - These are manual verification tools, not automated tests

## Relationship to Manual QA

```
Backend Processing → Manual Test Scripts → Visual QA Checklist
     (automated)         (sanity checks)      (human review)
```

**Workflow**:
1. Run manual test scripts (5 min) → Confirms backend succeeded
2. Open formatted DOCX (15 min) → Visual formatting review
3. Complete QA checklist (10 min) → Desk-rejection risk assessment

See: `brain/manual_qa_checklist.md` for full publisher-grade QA process

## Maintenance

- Update scripts when backend contracts change
- Add new scripts for new pipeline stages
- Keep scripts simple and focused on single concerns
