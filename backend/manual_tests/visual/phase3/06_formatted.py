import os
import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.pipeline.orchestrator import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="ScholarForm AI Visual Final Test")
    parser.add_argument("input_path", help="Path to input docx")
    parser.add_argument("--template", default="IEEE", help="Template to use")
    args = parser.parse_args()

    print(f"Generating formatted output for {args.input_path}")
    
    # 1. Pipeline Execution
    processor = DocumentProcessor()
    result = processor.process_and_format_document(args.input_path, template_name=args.template)
    
    # 2. Check Result
    output_path = result.metadata.generated_doc_path
    
    if output_path and os.path.exists(output_path):
        target_dir = Path("manual_tests/visual_outputs")
        target_dir.mkdir(parents=True, exist_ok=True)
        final_file = target_dir / "06_formatted.docx"
        
        import shutil
        shutil.copy2(output_path, final_file)
        
        print(f"Done. Formatted document saved to {final_file}")
    else:
        print(f"❌ ERROR: Generation failed.")

if __name__ == "__main__":
    main()
