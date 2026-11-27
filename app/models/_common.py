"""Helpers shared by all model modules."""

import uuid


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def new_uuid() -> str:
    return str(uuid.uuid4())
