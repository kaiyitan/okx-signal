import logging
import aiohttp
from app.config import settings
from app.cache import redis_client

logger = logging.getLogger(__name__)


async def _fetch_coingecko_top100(session: aiohttp.ClientSession) -> list[str]:
    url = f"{settings.coingecko_api_url}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
    }
    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        data = await resp.json()

    if settings.cache_raw_response:
        await redis_client.cache_raw_response("coingecko:top100", data)

    return [coin["symbol"].upper() for coin in data]


async def _fetch_okx_spot_instids(session: aiohttp.ClientSession) -> set[str]:
    url = f"{settings.okx_rest_url}/api/v5/market/tickers"
    params = {"instType": "SPOT"}
    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        data = await resp.json()

    if settings.cache_raw_response:
        await redis_client.cache_raw_response("okx:spot:tickers", data)

    return {t["instId"] for t in data.get("data", [])}


async def build_universe() -> list[str]:
    async with aiohttp.ClientSession() as session:
        top100 = await _fetch_coingecko_top100(session)
        okx_instids = await _fetch_okx_spot_instids(session)

    matched = [f"{sym}-USDT" for sym in top100 if f"{sym}-USDT" in okx_instids]
    logger.info(f"Universe: {len(matched)} symbols matched on OKX SPOT")

    await redis_client.set_symbols(matched)
    return matched
