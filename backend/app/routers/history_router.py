from typing import Optional
from fastapi import APIRouter
from app.repositories import history as repo
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50, window_id: Optional[int] = None):
    return {"items": repo.list_runs(limit, window_id)}
