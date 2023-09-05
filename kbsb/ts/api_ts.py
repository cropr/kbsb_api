from fastapi import APIRouter
from .ts import setup_series

router = APIRouter(prefix="/api/ts")


@router.get("/")
def ts_info():
    return "Test setup"


@router.get("/series")
async def api_setup_series():
    await setup_series()
    return "OK"
