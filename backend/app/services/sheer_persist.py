"""Shape sheer dual-layer payloads for history storage and open views."""

from __future__ import annotations

from copy import deepcopy


def sheer_enabled(result: dict) -> bool:
    sheer = result.get("sheer")
    return isinstance(sheer, dict) and bool(sheer.get("enabled"))


def merge_sheer_into_main(snapshot: dict) -> dict:
    """Keep sheer switch / fabric meta; fold sheer meters into the main line."""
    if not isinstance(snapshot, dict):
        return snapshot
    out = deepcopy(snapshot)
    if not sheer_enabled(out):
        return out
    sheer = dict(out.get("sheer") or {})
    sheer_m = float(sheer.get("meters") or 0)
    main_m = float(out.get("meters") or 0)
    out["list_sheer_meters"] = sheer_m
    out["list_main_meters"] = main_m
    out["meters"] = round(main_m + sheer_m, 2)
    sheer["meters"] = 0.0
    sheer["panels"] = sheer.get("panels") if sheer.get("panels") == 0 else 0
    sheer["cut_height"] = sheer.get("cut_height") if sheer.get("cut_height") == 0 else 0.0
    out["sheer"] = sheer
    out["sheer_merged"] = True
    return out


def open_drop_sheer(result: dict) -> dict:
    """Open path keeps sheer.enabled, but drops sheer meters (or merges into main)."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not sheer_enabled(out):
        return out
    if out.get("sheer_merged") or "list_sheer_meters" in out:
        sheer = dict(out.get("sheer") or {})
        sheer["meters"] = 0.0
        out["sheer"] = sheer
        return out
    return merge_sheer_into_main(out)


def list_summary_view(result: dict) -> dict:
    """List may surface stashed sheer meters via list_sheer_meters while sheer.meters is 0."""
    out = open_drop_sheer(result)
    return out


def summarize_sheer(result: dict) -> dict:
    """Flat view of sheer switch / side meters for open consumers."""
    if not isinstance(result, dict):
        return {}
    sheer = result.get("sheer") or {}
    return {
        "enabled": bool(sheer.get("enabled")),
        "sheer_meters": sheer.get("meters"),
        "list_sheer_meters": result.get("list_sheer_meters"),
        "meters": result.get("meters"),
        "sheer_merged": bool(result.get("sheer_merged")),
    }
