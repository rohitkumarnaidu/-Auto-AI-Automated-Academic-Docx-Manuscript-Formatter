# Backend Testing

<cite>
**Referenced Files in This Document**
- [pytest.ini](file://backend/pytest.ini)
- [pyproject.toml](file://backend/pyproject.toml)
- [conftest.py](file://backend/tests/conftest.py)
- [integration/conftest.py](file://backend/tests/integration/conftest.py)
- [test_scibert_benchmark.py](file://backend/tests/test_scibert_benchmark.py)
- [test_formatter_golden_files.py](file://backend/tests/test_formatter_golden_files.py)
- [labels.json](file://backend/tests/fixtures/scibert/labels.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document describes the backend testing strategy and infrastructure for the ScholarForm AI project. It focuses on pytest-based unit and integration testing, marker-based categorization, configuration via pytest.ini and pyproject.toml, and practical guidance for writing, running, and maintaining reliable backend tests. The repository includes approximately 46 backend test files organized across unit, integration, golden file, security, and SciBERT benchmark categories, along with supporting fixtures and CI integration.

## Project Structure
The backend test suite is organized under the backend/tests directory with the following high-level structure:
- Root-level pytest configuration and global fixtures
- Integration tests with dedicated fixtures and collection modifiers
- Golden file tests validating rendering outputs against expected structures
- SciBERT benchmark tests evaluating semantic parsing performance
- Additional categories such as security, performance, and contract tests

Key configuration and fixtures:
- pytest.ini defines test discovery, asyncio mode, warnings filtering, and markers
- pyproject.toml defines the Python packaging metadata for the backend
- Global conftest.py provides shared fixtures and automatic service availability checks
- Integration-specific conftest.py enforces service readiness and auto-applies integration markers

```mermaid
graph TB
A["pytest.ini<br/>Discovery, asyncio_mode, markers, warnings"] --> B["tests/"]
C["pyproject.toml<br/>Packaging metadata"] --> B
D["tests/conftest.py<br/>Global fixtures, service checks, mocks"] --> B
E["tests/integration/conftest.py<br/>Integration service checks, markers"] --> B
F["Golden file tests<br/>test_formatter_golden_files.py"] --> B
G["SciBERT benchmark<br/>test_scibert_benchmark.py"] --> B
H["Fixtures<br/>labels.json (SciBERT)"] --> G
```

**Diagram sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [pyproject.toml:1-9](file://backend/pyproject.toml#L1-L9)
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)
- [test_formatter_golden_files.py:1-253](file://backend/tests/test_formatter_golden_files.py#L1-L253)
- [test_scibert_benchmark.py:1-92](file://backend/tests/test_scibert_benchmark.py#L1-L92)
- [labels.json:1-203](file://backend/tests/fixtures/scibert/labels.json#L1-L203)

**Section sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [pyproject.toml:1-9](file://backend/pyproject.toml#L1-L9)
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)

## Core Components
- Test discovery and execution
  - pytest.ini sets testpaths to tests, excludes scripts and manual test directories, and enables asyncio_mode = auto for async test support.
  - Python naming conventions are defined for files, classes, and functions to streamline discovery.
  - addopts configures verbose output, concise traceback, and disables a third-party plugin.
  - filterwarnings suppresses known deprecation warnings to keep logs focused.
- Markers
  - The marker set includes unit, integration, performance, llm, service, regression, database, contract, pipeline, slow, and rag. These enable selective runs and categorization.
- Global fixtures and service checks
  - conftest.py inserts the backend root into sys.path, ensures the working directory is correct, and provides:
    - Automatic skipping of integration tests when required services are unreachable
    - Global Redis mocking for caching, rate limiting, and streaming publish
    - Document fixtures for minimal and full PipelineDocument instances
- Integration fixtures and markers
  - integration/conftest.py validates Redis and GROBID availability and auto-applies the integration marker to tests under tests/integration.

**Section sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)

## Architecture Overview
The backend testing architecture centers on pytest with layered fixtures and environment-aware skipping. Integration tests are gated by service availability, while global fixtures standardize mocking and document construction. Golden file tests validate rendering outputs, and SciBERT benchmark tests evaluate semantic parsing accuracy.

```mermaid
graph TB
subgraph "pytest Runtime"
P1["pytest.ini<br/>markers, asyncio_mode, warnings"]
P2["pyproject.toml<br/>packaging"]
end
subgraph "Global Fixtures"
F1["conftest.py<br/>service checks, Redis mocks, document fixtures"]
end
subgraph "Integration Layer"
I1["integration/conftest.py<br/>service checks, integration marker"]
end
subgraph "Test Suites"
T1["Golden file tests"]
T2["SciBERT benchmark"]
T3["Unit & Other Tests"]
end
P1 --> F1
P2 --> F1
F1 --> T3
I1 --> T1
I1 --> T2
```

**Diagram sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [pyproject.toml:1-9](file://backend/pyproject.toml#L1-L9)
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)
- [test_formatter_golden_files.py:1-253](file://backend/tests/test_formatter_golden_files.py#L1-L253)
- [test_scibert_benchmark.py:1-92](file://backend/tests/test_scibert_benchmark.py#L1-L92)

## Detailed Component Analysis

### Golden File Tests
Purpose:
- Validate that formatted Word outputs match expected structural characteristics for multiple citation templates.

Key behaviors:
- Loads Markdown samples enriched with YAML frontmatter and constructs PipelineDocument instances programmatically.
- Uses the Formatter to render DOCX outputs and extracts structural summaries (section counts, heading hierarchy presence, template metadata, reference counts).
- Compares actual vs. expected structural summaries and asserts equality per template.

Execution strategy:
- Run with pytest in the tests directory; relies on global fixtures for environment setup.
- Outputs are written to a temporary directory per test run for inspection.

```mermaid
sequenceDiagram
participant Py as "pytest"
participant GF as "test_formatter_golden_files.py"
participant FM as "Formatter"
participant FS as "File System"
Py->>GF : "Discover and run test"
GF->>FS : "Load golden JSON and Markdown sample"
GF->>GF : "Build PipelineDocument"
GF->>FM : "format(document, template_name)"
FM-->>GF : "DOCX Bytes"
GF->>FS : "Save to tmp_path"
GF->>FS : "Parse DOCX and compute summary"
GF-->>Py : "Assert structural summary equals expected"
```

**Diagram sources**
- [test_formatter_golden_files.py:222-253](file://backend/tests/test_formatter_golden_files.py#L222-L253)

**Section sources**
- [test_formatter_golden_files.py:1-253](file://backend/tests/test_formatter_golden_files.py#L1-L253)

### SciBERT Benchmark Tests
Purpose:
- Evaluate semantic parsing performance using a curated set of academic papers and macro-F1 thresholds.

Key behaviors:
- Loads fixture labels from labels.json and iterates over Markdown samples to parse and classify blocks.
- Configures USE_SCIBERT_CLASSIFICATION and resolves a model name from environment or fallback.
- Computes per-paper and overall macro-F1 scores and asserts minimum thresholds.

Execution strategy:
- Requires an LLM/runtime capable of serving the chosen SciBERT model; marked with llm, service, and slow.
- Skips when fixtures are missing or when a suitable parser is unavailable.

```mermaid
flowchart TD
Start(["Start SciBERT Benchmark"]) --> LoadLabels["Load labels.json"]
LoadLabels --> CheckSamples{"Samples available?"}
CheckSamples --> |No| Skip["Skip test"]
CheckSamples --> |Yes| ResolveModel["Resolve benchmark model"]
ResolveModel --> InitParser["Initialize ParserFactory"]
InitParser --> IteratePapers["Iterate samples"]
IteratePapers --> ParseDoc["Parse paper to PipelineDocument"]
ParseDoc --> Classify["SemanticParser.analyze_blocks()"]
Classify --> ComputeF1["Compute per-paper macro-F1"]
ComputeF1 --> Aggregate["Aggregate overall true/predicted labels"]
Aggregate --> AssertMin["Assert overall macro-F1 >= threshold"]
AssertMin --> End(["End"])
Skip --> End
```

**Diagram sources**
- [test_scibert_benchmark.py:46-92](file://backend/tests/test_scibert_benchmark.py#L46-L92)
- [labels.json:1-203](file://backend/tests/fixtures/scibert/labels.json#L1-L203)

**Section sources**
- [test_scibert_benchmark.py:1-92](file://backend/tests/test_scibert_benchmark.py#L1-L92)
- [labels.json:1-203](file://backend/tests/fixtures/scibert/labels.json#L1-L203)

### Integration Test Infrastructure
Purpose:
- Ensure integration tests only run when required services are reachable and automatically apply the integration marker.

Key behaviors:
- Validates Redis and GROBID availability using socket connections with timeouts.
- Auto-skips tests when services are down.
- Applies the integration marker to tests under tests/integration during collection.

```mermaid
flowchart TD
A["Collect items"] --> B["Check path for '/tests/integration/'"]
B --> |Yes| C["Add marker 'integration'"]
B --> |No| D["Leave unmarked"]
C --> E["Run service reachability checks"]
D --> E
E --> F{"Services available?"}
F --> |No| G["Skip test"]
F --> |Yes| H["Execute test"]
```

**Diagram sources**
- [integration/conftest.py:35-41](file://backend/tests/integration/conftest.py#L35-L41)
- [integration/conftest.py:24-33](file://backend/tests/integration/conftest.py#L24-L33)

**Section sources**
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)

### Global Fixtures and Mocking Strategy
Purpose:
- Provide consistent environment setup, document fixtures, and global mocking for Redis-dependent components.

Key behaviors:
- Inserts backend root into sys.path and sets working directory to backend root.
- Automatically skips integration tests when Redis/GROBID are unreachable.
- Globally mocks:
  - Streaming publish for real-time events
  - Rate limiter Redis client
  - Cache Redis client
- Supplies minimal and full PipelineDocument fixtures for tests requiring structured documents.

```mermaid
classDiagram
class GlobalFixtures {
+insert_backend_root()
+ensure_working_dir()
+skip_integration_when_services_unavailable()
+mock_redis()
+minimal_doc() PipelineDocument
+full_doc(minimal_doc) PipelineDocument
}
```

**Diagram sources**
- [conftest.py:37-58](file://backend/tests/conftest.py#L37-L58)
- [conftest.py:72-111](file://backend/tests/conftest.py#L72-L111)

**Section sources**
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)

## Dependency Analysis
Markers and configuration dependencies:
- pytest.ini controls discovery, asyncio_mode, warnings, and marker definitions.
- Global conftest.py depends on environment variables for service endpoints and applies automatic skipping and mocking.
- Integration conftest.py depends on environment variables and socket connectivity to gate tests.

```mermaid
graph LR
PI["pytest.ini"] --> CF["tests/conftest.py"]
PI --> IC["tests/integration/conftest.py"]
PY["pyproject.toml"] --> CF
CF --> |"mocks"| Redis["Redis clients"]
CF --> |"mocks"| Stream["Streaming publish"]
CF --> |"fixtures"| Docs["PipelineDocument fixtures"]
IC --> |"marker"| IT["Integration tests"]
```

**Diagram sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [pyproject.toml:1-9](file://backend/pyproject.toml#L1-L9)
- [conftest.py:37-58](file://backend/tests/conftest.py#L37-L58)
- [integration/conftest.py:35-41](file://backend/tests/integration/conftest.py#L35-L41)

**Section sources**
- [pytest.ini:1-28](file://backend/pytest.ini#L1-L28)
- [pyproject.toml:1-9](file://backend/pyproject.toml#L1-L9)
- [conftest.py:1-112](file://backend/tests/conftest.py#L1-L112)
- [integration/conftest.py:1-41](file://backend/tests/integration/conftest.py#L1-L41)

## Performance Considerations
- Asyncio mode
  - asyncio_mode = auto in pytest.ini supports async test functions and fixtures without manual event loop management.
- Warning filtering
  - filterwarnings reduces noise from known deprecations, improving readability and reducing CI log volume.
- Test categorization
  - Use markers to selectively run subsets (e.g., unit, integration, slow) and avoid unnecessary heavy workloads.
- Fixture reuse
  - Global fixtures minimize repeated setup costs and ensure consistent environments across tests.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- Integration tests skipped unexpectedly
  - Cause: Required services (Redis, GROBID) unreachable.
  - Resolution: Verify REDIS_HOST/REDIS_PORT and GROBID_HOST/GROBID_PORT environment variables and service availability.
- SciBERT benchmark failures
  - Cause: Missing labels.json fixtures or unsupported parser for a sample.
  - Resolution: Ensure fixtures exist and a suitable parser is available; optionally set SCIBERT_BENCHMARK_MODEL to a reachable model.
- Golden file mismatches
  - Cause: Changes in rendering logic affecting structural summaries.
  - Resolution: Regenerate golden outputs only after confirming intended behavioral changes; otherwise, investigate differences in heading hierarchy, reference counts, or template metadata.
- Global Redis mocks interfering with specific tests
  - Cause: Tests expecting real Redis behavior.
  - Resolution: Temporarily disable global mocks or isolate tests that require real Redis interactions.

**Section sources**
- [conftest.py:37-58](file://backend/tests/conftest.py#L37-L58)
- [integration/conftest.py:24-33](file://backend/tests/integration/conftest.py#L24-L33)
- [test_scibert_benchmark.py:34-36](file://backend/tests/test_scibert_benchmark.py#L34-L36)
- [test_formatter_golden_files.py:237-253](file://backend/tests/test_formatter_golden_files.py#L237-L253)

## Conclusion
The backend testing framework leverages pytest with carefully designed markers, global fixtures, and environment-aware gating to support reliable unit and integration testing. Golden file and SciBERT benchmark tests ensure rendering correctness and model performance, respectively. By adhering to the documented configuration and execution strategies, contributors can write, run, and maintain robust backend tests across diverse environments.