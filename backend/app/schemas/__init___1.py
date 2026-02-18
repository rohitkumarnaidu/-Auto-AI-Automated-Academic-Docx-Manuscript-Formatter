"""
app/schemas/__init___1.py

Extended package init — mirrors __init__.py but also exposes
internal helpers and type aliases for use in tests and advanced tooling.

This file exists as a versioned snapshot of the schema registry.
Import from __init__.py for normal use; use this file when you need
access to the extended type aliases and validators directly.
"""

# Re-export everything from the main __init__
from app.schemas import *  # noqa: F401, F403
from app.schemas import __all__  # noqa: F401

# Additional internal helpers exposed for testing and tooling
from app.schemas.auth import _validate_password_strength  # noqa: F401
from app.schemas.document import (  # noqa: F401
    ExportFormat,
    DocumentStatus,
    PageSize,
    TemplateChoice,
)
from app.schemas.document_1 import (  # noqa: F401
    BatchUploadItem,
)
from app.schemas.user_1 import (  # noqa: F401
    NotificationPreferences,
)
