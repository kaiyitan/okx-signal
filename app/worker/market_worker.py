import asyncio
import json
import logging
import aiohttp
import websockets
from app.config import settings
from app.cache import redis_client
from app.engine.ema import calculate_ema
from app.engine.signal_engine import process_daily_candle, process_intraday_candle

logger = logging.getLogger(__name__)

CHANNELS = ["candle1D", "candle15m", "candle1H"]
WS_MAX_ARGS = 240  # OKX limit per connection


def _parse_candle(raw: list) -> dict:
    return {
        "ts": raw[0],
        "open": raw[1],
        "high": raw[2],
        "low": raw[3],
        "close": raw[4],
        "vol": raw[5],
        "confirm": raw[8],
    }


async def _bootstrap_symbol(instId: str, session: aiohttp.ClientSession):
    url = f"{settings.okx_rest_url}/api/v5/market/candles"
    params = {"instId": instId, "bar": "1D", "limit": "100"}

    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        data = await resp.json()

    if settings.cache_raw_response:
        await redis_client.cache_raw_response(f"okx:candles:{instId}:1D", data)

    candles = data.get("data", [])
    if not candles:
        logger.warning(f"No daily candles for {instId}")
        return

    # OKX returns newest first — reverse for chronological EMA
    candles_asc = list(reversed(candles))
    closes = [float(c[4]) for c in candles_asc]

    ema20 = calculate_ema(closes)
    if ema20:
        await redis_client.set_ema20(instId, ema20)

    await redis_client.set_daily_close(instId, closes[-1])

    for c in candles_asc[-10:]:
        await redis_client.push_daily_candle(instId, _parse_candle(c))


async def _handle_message(msg: str):
    try:
        data = json.loads(msg)
    except json.JSONDecodeError:
        return

    if "arg" not in data or "data" not in data:
        return

    channel = data["arg"]["channel"]
    instId = data["arg"]["instId"]
    candle = _parse_candle(data["data"][0])

    if channel == "candle1D":
        await process_daily_candle(instId, candle)
    elif channel in ("candle15m", "candle1H"):
        timeframe = channel.replace("candle", "")
        await process_intraday_candle(instId, timeframe, candle)


async def _run_ws_connection(args: list[dict]):
    while True:
        try:
            async with websockets.connect(settings.okx_ws_url, ping_interval=20) as ws:
                await ws.send(json.dumps({"op": "subscribe", "args": args}))
                logger.info(f"WS subscribed: {len(args)} channels")
                async for msg in ws:
                    await _handle_message(msg)
        except Exception as e:
            logger.error(f"WS error: {e}, reconnecting in 5s")
            await asyncio.sleep(5)


async def run_market_worker(symbols: list[str]):
    logger.info(f"Bootstrapping {len(symbols)} symbols from OKX REST...")
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[_bootstrap_symbol(s, session) for s in symbols])
    logger.info("Bootstrap complete, starting WebSocket...")

    all_args = [
        {"channel": ch, "instId": sym}
        for sym in symbols
        for ch in CHANNELS
    ]

    # Split into batches respecting OKX per-connection limit
    batches = [all_args[i:i + WS_MAX_ARGS] for i in range(0, len(all_args), WS_MAX_ARGS)]
    await asyncio.gather(*[_run_ws_connection(batch) for batch in batches])
