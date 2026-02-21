
import re

with open(r'c:\Hackathons\ECLearnIX\(Auto AI) Automated Academic Docx Manuscript Formatter\automated-manuscript-formatter\backend\requirements.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    line = line.strip()
    if line:
        print(f"{i+1}: '{line}'")
