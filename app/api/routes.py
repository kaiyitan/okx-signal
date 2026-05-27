from fastapi import APIRouter, HTTPException
from app.cache import redis_client

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/symbols")
async def get_symbols():
    return await redis_client.get_symbols()


@router.get("/signals")
async def get_signals():
    return await redis_client.get_all_signals()


@router.get("/signals/{symbol}")
async def get_signal(symbol: str):
    instId = symbol.upper()
    signal = await redis_client.get_signal(instId)
    if not signal:
        raise HTTPException(status_code=404, detail=f"No signal for {instId}")
    return signal
