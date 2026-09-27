"""0-1 sheer layer: second track computed alongside the main curtain."""
from app.engines.curtain_math import fabric_meters


def sheer_meters(window_w, window_h, fullness, hem_top, hem_bottom, fabric_width) -> dict:
    if fullness is None or float(fullness) <= 0:
        raise ValueError("sheer fullness required")
    if fabric_width is None or float(fabric_width) <= 0:
        raise ValueError("fabric width required")
    return fabric_meters(window_w, window_h, float(fullness), hem_top, hem_bottom, fabric_width)

# Open-path / persist readers may reshape sheer meters independently.
