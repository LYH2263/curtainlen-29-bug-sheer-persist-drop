from typing import Optional
from pydantic import BaseModel

class EstimateRequest(BaseModel):
    window_id: int
    fabric_id: int
    save: bool = False
    note: str = ""
    sheer_enabled: bool = False
    sheer_fabric_id: Optional[int] = None
    sheer_fullness: Optional[float] = None
