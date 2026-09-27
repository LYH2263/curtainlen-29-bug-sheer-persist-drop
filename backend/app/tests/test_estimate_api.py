from app.db import connect
from app.engines.curtain_math import fabric_meters

MAIN_KEYS = ["finished_width", "panels", "cut_height", "meters", "fabric_width"]
MAIN_EXPECTED = {"finished_width": 6.0, "panels": 5, "cut_height": 2.85, "meters": 14.25, "fabric_width": 1.4}
SHEER_EXPECTED = {"enabled": True, "fabric_id": 2, "fabric_name": "纱帘2.8m",
                  "fullness": 2.0, "fabric_width": 2.8, "finished_width": 6.0,
                  "panels": 3, "cut_height": 2.8, "meters": 8.4}
DISABLED_SHEER = {"enabled": False, "fabric_id": None, "fabric_name": None,
                  "fullness": 0.0, "fabric_width": 0.0, "finished_width": 0.0,
                  "panels": 0, "cut_height": 0.0, "meters": 0.0}


def runs(client, **params):
    qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    return client.get("/api/runs" + qs).json()["items"]


def assert_no_runs(client):
    assert runs(client) == []


def test_get_dry_run_main_only(client):
    r = client.get("/api/estimate?window_id=1&fabric_id=1")
    assert r.status_code == 200
    out = r.json()
    for k in MAIN_KEYS:
        assert out[k] == MAIN_EXPECTED[k]
    assert out["run_id"] is None
    assert out["fullness"] == 2.0
    assert out["sheer"] == DISABLED_SHEER
    assert_no_runs(client)


def test_post_dry_run_sheer_off_with_stray_params(client):
    r = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1,
                                           "sheer_enabled": False,
                                           "sheer_fabric_id": 2, "sheer_fullness": 0})
    assert r.status_code == 200
    out = r.json()
    for k in MAIN_KEYS:
        assert out[k] == MAIN_EXPECTED[k]
    assert out["sheer"] == DISABLED_SHEER
    assert_no_runs(client)


def test_save_both_layers_one_row(client):
    r = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1, "save": True,
                                           "sheer_enabled": True,
                                           "sheer_fabric_id": 2, "sheer_fullness": 2.0})
    assert r.status_code == 200
    out = r.json()
    assert isinstance(out["run_id"], int)
    for k in MAIN_KEYS:
        assert out[k] == MAIN_EXPECTED[k]
    for k, v in SHEER_EXPECTED.items():
        assert out["sheer"][k] == v
    win_runs = runs(client, window_id=1)
    assert len(win_runs) == 1
    assert len(runs(client)) == 1
    saved = win_runs[0]["result"]
    for k in MAIN_KEYS:
        assert saved[k] == MAIN_EXPECTED[k]
    for k, v in SHEER_EXPECTED.items():
        assert saved["sheer"][k] == v


def test_invalid_sheer_matrix(client):
    gets = [
        "/api/estimate?window_id=1&fabric_id=1&save=true&sheer=true",
        "/api/estimate?window_id=1&fabric_id=1&sheer=true&sheer_fabric_id=2",
        "/api/estimate?window_id=1&fabric_id=1&sheer=true&sheer_fabric_id=2&sheer_fullness=0",
        "/api/estimate?window_id=1&fabric_id=1&sheer=true&sheer_fabric_id=2&sheer_fullness=-1",
    ]
    for path in gets:
        assert client.get(path).status_code == 422, path
    posts = [
        {"window_id": 1, "fabric_id": 1, "save": True, "sheer_enabled": True},
        {"window_id": 1, "fabric_id": 1, "sheer_enabled": True, "sheer_fabric_id": 2},
        {"window_id": 1, "fabric_id": 1, "save": True, "sheer_enabled": True,
         "sheer_fabric_id": 2, "sheer_fullness": 0},
        {"window_id": 1, "fabric_id": 1, "sheer_enabled": True,
         "sheer_fabric_id": 2, "sheer_fullness": -1},
    ]
    for body in posts:
        assert client.post("/api/estimate", json=body).status_code == 422, body
    assert_no_runs(client)


def test_sheer_fabric_missing(client):
    r = client.get("/api/estimate?window_id=1&fabric_id=1&sheer=true&sheer_fabric_id=999&sheer_fullness=2")
    assert r.status_code == 404
    assert_no_runs(client)


def test_dirty_sheer_fabric(client):
    r = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1,
                                           "sheer_enabled": True,
                                           "sheer_fabric_id": 3, "sheer_fullness": 2.0})
    assert r.status_code == 422
    assert "dirty sheer fabric" in r.json()["detail"]
    assert_no_runs(client)


def test_dirty_main_fabric_now_422_not_500(client):
    r = client.get("/api/estimate?window_id=1&fabric_id=3")
    assert r.status_code == 422
    assert "fabric width required" in r.json()["detail"]
    assert_no_runs(client)


def test_dirty_window_and_missing_refs(client):
    assert client.get("/api/estimate?window_id=3&fabric_id=1").status_code == 422
    assert client.get("/api/estimate?window_id=999&fabric_id=1").status_code == 404
    assert client.get("/api/estimate?window_id=1&fabric_id=999").status_code == 404
    assert_no_runs(client)


def test_saved_run_pinned_after_fabric_width_change(client):
    r = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1, "save": True,
                                           "sheer_enabled": True,
                                           "sheer_fabric_id": 2, "sheer_fullness": 2.0})
    assert r.status_code == 200
    c = connect()
    try:
        c.execute("UPDATE fabrics SET fabric_width=1.5 WHERE id=1")
        c.execute("UPDATE fabrics SET fabric_width=3.0 WHERE id=2")
        c.commit()
    finally:
        c.close()
    try:
        saved = runs(client, window_id=1)[0]["result"]
        assert saved["panels"] == 5
        assert saved["meters"] == 14.25
        assert saved["fabric_width"] == 1.4
        assert saved["sheer"]["panels"] == 3
        assert saved["sheer"]["meters"] == 8.4
        assert saved["sheer"]["fabric_width"] == 2.8
        live = client.get("/api/estimate?window_id=1&fabric_id=1").json()
        assert live["panels"] == 4
        assert live["meters"] == 11.4
        assert fabric_meters(3.0, 2.6, 2.0, 0.08, 0.12, 3.0)["panels"] == 2
    finally:
        c = connect()
        try:
            c.execute("UPDATE fabrics SET fabric_width=1.4 WHERE id=1")
            c.execute("UPDATE fabrics SET fabric_width=2.8 WHERE id=2")
            c.commit()
        finally:
            c.close()


def test_disabled_sheer_round_trip(client):
    r = client.post("/api/estimate", json={"window_id": 1, "fabric_id": 1, "save": True})
    assert r.status_code == 200
    saved = runs(client)[0]["result"]
    assert saved["sheer"] == DISABLED_SHEER
