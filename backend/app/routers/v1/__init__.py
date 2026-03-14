from __future__ import annotations

from fastapi import APIRouter

from . import documents, generator, health, synthesis, templates

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health.router, prefix="/health", tags=["Health v1"])
v1_router.include_router(documents.router, prefix="/documents", tags=["Documents v1"])
v1_router.include_router(templates.router, prefix="/templates", tags=["Templates v1"])
v1_router.include_router(generator.router, prefix="/generator", tags=["Generator v1"])
v1_router.include_router(synthesis.router, prefix="/synthesis", tags=["Synthesis v1"])
