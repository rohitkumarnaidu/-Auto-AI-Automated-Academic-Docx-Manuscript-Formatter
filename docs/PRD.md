# ScholarForm AI — Product Requirements Document (PRD)

## Product Vision
ScholarForm AI is a web-based academic manuscript formatting and AI document generation platform. It empowers academic researchers, students, and professionals to produce journal-compliant documents without LaTeX knowledge.

## Two Products, Four Modes

### Product 1 — Document Formatter
| Mode | Description | Status |
|------|-------------|--------|
| **Mode A: Upload & Format** | Upload any document → select journal template → download formatted DOCX/PDF | ~60% Done |
| **Mode B: Live Preview Editor** | Split-screen TipTap editor with real-time HTML preview, template switching, AI sidebar | ~85% Files |

### Product 2 — AI Document Generator
| Mode | Description | Status |
|------|-------------|--------|
| **Mode A: Multi-Doc Synthesis** | Upload 2-6 papers → AI reads all → removes duplicates → generates synthesis | ~80% Files |
| **Mode B: AI Agent** | Chat-based: user describes paper → AI plans → generates outline → writes sections → refines | ~90% Files |

## Target Users
| Persona | Need | Key Flow |
|---------|------|----------|
| **PhD Student** | Format thesis for IEEE/ACM submission | Upload → Select IEEE → Download formatted |
| **Research Professor** | Generate literature review from multiple papers | Multi-upload → Synthesis → Review → Export |
| **Undergraduate** | Write a first research paper guided by AI | Chat with Agent → Outline → Generate → Edit |
| **Journal Editor** | Check formatting compliance | Upload → Quality score → Fix suggestions |
| **Guest User** | Quick format without account (5/day limit) | Upload → Process → Download (no login) |

## KPIs
| Metric | Target |
|--------|--------|
| Guest → Signup conversion | >15% |
| Upload → Download completion rate | >80% |
| Average generation quality score | >70% |
| P99 upload ACK latency | <400ms |
| P99 live preview RTT | <200ms |
| Monthly active users (6 months) | 1,000+ |

## Supported Templates (17)
IEEE, ACM, APA, MLA, Chicago, Harvard, Vancouver, Springer, Nature, Elsevier, Numeric, Modern Blue, Modern Gold, Modern Red, None, Resume, Portfolio

## Supported Input Formats (9)
DOCX, PDF (via GROBID), ODT, TeX, HTML, Markdown, TXT, RTF, DOC

## Supported Export Formats
DOCX, PDF (via LibreOffice), LaTeX (via Pandoc)
