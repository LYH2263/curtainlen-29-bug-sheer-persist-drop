"""Dual-layer snapshot shaping.

The main curtain and the sheer layer are TWO separate meter lines. The stored
snapshot is exactly the estimate response payload, and every reader (history
list, window detail / re-open) returns it unchanged. Sheer meters must never be
folded into the main line and ``sheer.meters`` must never be zeroed while
``sheer.enabled`` stays true.
"""

from __future__ import annotations

from copy import deepcopy


def sheer_enabled(result: dict) -> bool:
    sheer = result.get("sheer") if isinstance(result, dict) else None
    return isinstance(sheer, dict) and bool(sheer.get("enabled"))


def persist_snapshot(result: dict) -> dict:
    """Canonical stored shape: identical to the estimate response (split tracks)."""
    return deepcopy(result)


# Open / list readers return the stored snapshot verbatim so that re-opening a
# run shows precisely the main/sheer meters confirmed at write time.
read_snapshot = persist_snapshot
open_view = persist_snapshot


def summarize_sheer(result: dict) -> dict:
    """Flat view of the sheer switch and the two separate meter lines."""
    if not isinstance(result, dict):
        return {}
    sheer = result.get("sheer") or {}
    return {
        "enabled": bool(sheer.get("enabled")),
        "sheer_meters": sheer.get("meters"),
        "meters": result.get("meters"),
    }
