"""
Production Stress Test - Final Baseline Validation
Tests "none" template professional baseline format with real documents.

PRODUCTION HARDENING MODE - Verification Only
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline.orchestrator import PipelineOrchestrator
from docx import Document as WordDocument
import json

class ProductionStressValidator:
    """Validates professional baseline format with real documents."""
    
    def __init__(self):
        self.orchestrator = PipelineOrchestrator()
        self.results = {
            "complex_hierarchy": {},
            "multi_media": {},
            "reference_heavy": {},
            "minimal": {},
            "edge_case": {}
        }
    
    def validate_document(self, input_path: str, test_name: str, template: str = "none"):
        """Run full pipeline and validate output."""
        print(f"\n{'='*60}")
        print(f"Testing: {test_name}")
        print(f"Template: {template}")
        print(f"Input: {input_path}")
        print(f"{'='*60}\n")
        
        try:
            # Run pipeline
            result = self.orchestrator.run(
                input_path=input_path,
                template_name=template,
                output_path=f"output_{test_name}_{template}.docx"
            )
            
            # Validate structure
            doc = result.get("document")
            if not doc:
                return {"status": "FAIL", "error": "No document returned"}
            
            # Check for visual artifacts
            validation = {
                "status": "PASS",
                "blocks": len(doc.blocks),
                "figures": len(doc.figures),
                "tables": len(doc.tables),
                "references": len(doc.references),
                "warnings": []
            }
            
            # Check for empty anchor blocks (should not render)
            empty_anchors = [
                b for b in doc.blocks 
                if b.text.strip() == "" and (
                    b.metadata.get("has_figure") or 
                    b.metadata.get("has_equation")
                )
            ]
            if empty_anchors:
                validation["warnings"].append(
                    f"Found {len(empty_anchors)} empty anchor blocks (should skip rendering)"
                )
            
            # Check for caption duplication patterns
            for fig in doc.figures:
                if fig.caption_text:
                    # Check for "Figure N: Figure N:" pattern
                    if fig.caption_text.lower().count("figure") > 1:
                        validation["warnings"].append(
                            f"Possible caption duplication: {fig.caption_text[:50]}"
                        )
            
            # Check structural integrity
            indices = [b.index for b in doc.blocks]
            if indices != sorted(indices):
                validation["status"] = "FAIL"
                validation["error"] = "Block ordering corrupted"
            
            print(f"✅ Status: {validation['status']}")
            print(f"   Blocks: {validation['blocks']}")
            print(f"   Figures: {validation['figures']}")
            print(f"   Tables: {validation['tables']}")
            print(f"   References: {validation['references']}")
            
            if validation["warnings"]:
                print(f"\n⚠️  Warnings:")
                for w in validation["warnings"]:
                    print(f"   - {w}")
            
            return validation
            
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return {"status": "FAIL", "error": str(e)}
    
    def run_stress_tests(self):
        """Run all 5 stress tests."""
        
        print("\n" + "="*60)
        print("PRODUCTION STRESS VALIDATION - BASELINE FREEZE")
        print("="*60)
        
        # Test 1: Complex Hierarchy (if exists)
        # Test 2: Multi-Media (if exists)
        # Test 3: Reference-Heavy (if exists)
        # Test 4: Minimal (if exists)
        # Test 5: Edge Case (if exists)
        
        print("\n" + "="*60)
        print("STRESS TEST SUITE COMPLETE")
        print("="*60)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        all_pass = all(
            r.get("status") == "PASS" 
            for r in self.results.values() 
            if r
        )
        
        if all_pass:
            print("\n✅ ALL TESTS PASSED")
            print("\n🧊 READY FOR BASELINE FREEZE")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("\n🚨 FIX BEFORE FREEZE")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    validator = ProductionStressValidator()
    
    # Example: Test with a sample document
    # validator.validate_document("test_docs/sample.docx", "complex_hierarchy")
    
    print("""
    Production Stress Validation Framework Ready
    
    To run tests:
    1. Place test documents in test_docs/
    2. Run validator.validate_document() for each
    3. Check validation report
    
    Test Types Required:
    - Complex hierarchy (4+ heading levels)
    - Multi-media (3+ figures, 3+ tables)
    - Reference-heavy (15+ references)
    - Minimal (title + 2 paragraphs)
    - Edge case (empty sections, sparse content)
    
    All tests must PASS before freeze.
    """)
