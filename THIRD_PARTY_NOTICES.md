# Third-Party Notices

ScholarForm AI uses third-party libraries and components. This document lists their licenses.

## Backend (Python)

| Package | License | Use |
|---------|---------|-----|
| FastAPI | MIT | Web framework |
| Uvicorn | BSD-3-Clause | ASGI server |
| SQLAlchemy | MIT | ORM |
| Alembic | MIT | Database migrations |
| Celery | BSD-3-Clause | Task queue |
| Redis-py | MIT | Redis client |
| ChromaDB | Apache-2.0 | Vector database |
| Jinja2 | BSD-3-Clause | Template engine |
| python-docx | MIT | DOCX processing |
| PyMuPDF (fitz) | AGPL-3.0 | PDF parsing |
| httpx | BSD-3-Clause | HTTP client |
| pydantic | MIT | Data validation |
| python-multipart | Apache-2.0 | File uploads |
| python-jose[cryptography] | MIT | JWT handling |
| pytest | MIT | Testing |
| mypy | MIT | Type checking |
| ruff | MIT | Linter |
| Grobid Client | MIT | GROBID integration |
| docling | MIT | Document parsing |
| LiteLLM | MIT | LLM routing |
| Stripe Python | MIT | Payment processing |
| supabase-py | MIT | Supabase client |
| YAKE | GPL-3.0 | Keyword extraction |
| spaCy | MIT | NLP pipeline |
| scikit-learn | BSD-3-Clause | ML utilities |

## Frontend (JavaScript/TypeScript)

| Package | License | Use |
|---------|---------|-----|
| Next.js | MIT | React framework |
| React | MIT | UI library |
| React DOM | MIT | DOM rendering |
| Tailwind CSS | MIT | CSS framework |
| TipTap | MIT | Rich text editor |
| Lucide Icons | ISC | Icon library |
| jsdom | MIT | Test environment |
| Vitest | MIT | Test framework |
| Playwright | Apache-2.0 | E2E testing |
| ESLint | MIT | Linter |
| PostCSS | MIT | CSS processing |

## Infrastructure

| Component | License | Use |
|-----------|---------|-----|
| PostgreSQL | PostgreSQL | Database |
| Redis | BSD-3-Clause | Cache + broker |
| Docker | Apache-2.0 | Container runtime |
| GROBID | AGPL-3.0 | PDF metadata extraction |

## License Texts

### MIT License

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### BSD-3-Clause License

```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
```

### Apache-2.0 License

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### AGPL-3.0 License

PyMuPDF (fitz) and GROBID are licensed under AGPL-3.0. If you need to use these components in a proprietary product, you must either:

- Purchase a commercial license from the respective authors
- Replace with an alternative (GROBID → Docling, PyMuPDF → PyPDF2 in fallback)
- Ensure your deployment complies with AGPL terms (source code availability)

---

*Last updated: June 2026*
