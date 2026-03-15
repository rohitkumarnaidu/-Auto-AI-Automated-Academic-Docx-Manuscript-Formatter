# 003 - API Versioning Strategy

Status: Accepted

Context: Clients depend on stable APIs while the backend evolves rapidly.

Decision: Maintain versioned APIs under `/api/v1` and keep legacy endpoints with deprecation notices.

Consequences: New features ship in `/api/v1` first, and legacy routes remain available until explicitly deprecated and removed.
