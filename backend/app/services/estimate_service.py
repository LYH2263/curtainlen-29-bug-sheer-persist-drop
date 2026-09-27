from fastapi import HTTPException
from app.engines.curtain_math import fabric_meters
from app.modules.sheer_layer import sheer_meters
from app.repositories import fabrics, history, settings_repo, windows


def _disabled_sheer():
    return {"enabled": False, "fabric_id": None, "fabric_name": None,
            "fullness": 0.0, "fabric_width": 0.0, "finished_width": 0.0,
            "panels": 0, "cut_height": 0.0, "meters": 0.0}


def run_estimate(window_id, fabric_id, save, note,
                 sheer_enabled=False, sheer_fabric_id=None, sheer_fullness=None):
    w = windows.get_window(window_id)
    f = fabrics.get_fabric(fabric_id)
    if not w or not f:
        raise HTTPException(404, "not found")
    if w.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty window")
    sf = None
    if sheer_enabled:
        if sheer_fabric_id is None:
            raise HTTPException(422, "sheer fabric required")
        sf = fabrics.get_fabric(sheer_fabric_id)
        if not sf:
            raise HTTPException(404, "sheer fabric not found")
        if sf.get("data_quality") == "dirty":
            raise HTTPException(422, "dirty sheer fabric")
        if sheer_fullness is None:
            raise HTTPException(422, "sheer fullness required")
        if float(sheer_fullness) <= 0:
            raise HTTPException(422, "sheer fullness must be > 0")
    settings = settings_repo.get_all()
    fullness = float(w.get("fullness") or settings.get("default_fullness", 2.0))
    try:
        calc = fabric_meters(w["width"], w["height"], fullness, f["hem_top"], f["hem_bottom"], f["fabric_width"])
        scalc = sheer_meters(w["width"], w["height"], float(sheer_fullness),
                             sf["hem_top"], sf["hem_bottom"], sf["fabric_width"]) if sheer_enabled else None
    except ValueError as e:
        raise HTTPException(422, str(e))
    if sheer_enabled:
        sheer_block = {"enabled": True, "fabric_id": sf["id"], "fabric_name": sf["name"],
                       "fullness": float(sheer_fullness), **scalc}
    else:
        sheer_block = _disabled_sheer()
    result = {**calc, "fullness": fullness, "sheer": sheer_block}
    if save:
        # Store the exact calc snapshot: main and sheer meters stay on their
        # own rows, identical to what this response returns.
        run_id = history.insert_run(window_id, fabric_id, result, note)
        return {"window": w, "fabric": f, "run_id": run_id, **result}
    return {"window": w, "fabric": f, "run_id": None, **result}
