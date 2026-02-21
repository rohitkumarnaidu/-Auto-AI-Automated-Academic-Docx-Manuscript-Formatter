
import re

def parse_reqs_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    reqs = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Split on ==, >=, <=, >, <
        name = re.split('[<>=!]', line)[0].strip()
        if name:
            reqs.append(name)
    return sorted(list(set(reqs)), key=str.lower)

txt_path = r'c:\Hackathons\ECLearnIX\(Auto AI) Automated Academic Docx Manuscript Formatter\automated-manuscript-formatter\backend\requirements.txt'
md_path = r'c:\Hackathons\ECLearnIX\(Auto AI) Automated Academic Docx Manuscript Formatter\automated-manuscript-formatter\backend\requirements.md'

req_names = parse_reqs_txt(txt_path)

with open(md_path, 'w', encoding='utf-8') as f:
    for name in req_names:
        f.write(name + '\n')

print(f"Successfully wrote {len(req_names)} packages to requirements.md")
