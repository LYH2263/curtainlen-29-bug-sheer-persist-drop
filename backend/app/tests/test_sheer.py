import pytest
from app.modules.sheer_layer import sheer_meters


def test_sheer_living_room():
    r = sheer_meters(3.0, 2.6, 2.0, 0.08, 0.12, 2.8)
    assert r == {"finished_width": 6.0, "panels": 3, "cut_height": 2.8, "meters": 8.4, "fabric_width": 2.8}


def test_sheer_min_one_panel():
    r = sheer_meters(1.0, 2.0, 1.5, 0.0, 0.0, 2.8)
    assert r["panels"] == 1
    assert r["meters"] == 2.0


def test_sheer_fullness_zero():
    with pytest.raises(ValueError):
        sheer_meters(3.0, 2.6, 0.0, 0.08, 0.12, 2.8)


def test_sheer_fullness_none():
    with pytest.raises(ValueError):
        sheer_meters(3.0, 2.6, None, 0.08, 0.12, 2.8)


def test_sheer_fullness_negative():
    with pytest.raises(ValueError):
        sheer_meters(3.0, 2.6, -1.0, 0.08, 0.12, 2.8)


def test_sheer_width_zero():
    with pytest.raises(ValueError):
        sheer_meters(3.0, 2.6, 2.0, 0.1, 0.1, 0.0)


def test_sheer_width_none():
    with pytest.raises(ValueError):
        sheer_meters(3.0, 2.6, 2.0, 0.1, 0.1, None)
