
import re

def normalize(name):
    return name.replace('_', '-').lower()

def parse_reqs_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    reqs = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Split on ==, >=, <=, >, <
        name = re.split('[<>=!]', line)[0].strip()
        if name:
            reqs.add(normalize(name))
    return reqs

def parse_reqs_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    reqs = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Some lines might have comments or versions
        name = re.split('[<>=! ]', line)[0].strip()
        if name:
            reqs.add(normalize(name))
    return reqs

txt_path = r'c:\Hackathons\ECLearnIX\(Auto AI) Automated Academic Docx Manuscript Formatter\automated-manuscript-formatter\backend\requirements.txt'
md_path = r'c:\Hackathons\ECLearnIX\(Auto AI) Automated Academic Docx Manuscript Formatter\automated-manuscript-formatter\backend\requirements.md'

txt_reqs = parse_reqs_txt(txt_path)
md_reqs = parse_reqs_md(md_path)

print("--- In MD but not in TXT ---")
for r in sorted(md_reqs - txt_reqs):
    print(r)

print("\n--- In TXT but not in MD ---")
for r in sorted(txt_reqs - md_reqs):
    print(r)
