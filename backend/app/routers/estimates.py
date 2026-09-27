from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service
router = APIRouter()
@router.get("/estimate")
def get_est(window_id: int = Query(...), fabric_id: int = Query(...), save: bool = False,
            sheer: bool = False, sheer_fabric_id: Optional[int] = None,
            sheer_fullness: Optional[float] = None):
    return estimate_service.run_estimate(window_id, fabric_id, save, "",
                                         sheer, sheer_fabric_id, sheer_fullness)
@router.post("/estimate")
def post_est(body: EstimateRequest):
    return estimate_service.run_estimate(body.window_id, body.fabric_id, body.save, body.note,
                                         body.sheer_enabled, body.sheer_fabric_id, body.sheer_fullness)
