"""Atomic local JSON/report writing with no remote side effects."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
from typing import Any

def atomic_json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    contents = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=".saluteface-", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
