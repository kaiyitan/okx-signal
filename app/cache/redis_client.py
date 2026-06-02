import json
import redis.asyncio as aioredis
from app.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            ssl=settings.redis_ssl,
            decode_responses=True,
        )
    return _redis


async def set_ema20(instId: str, value: float):
    r = await get_redis()
    await r.set(f"ema20:{instId}", value)


async def get_ema20(instId: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"ema20:{instId}")
    return float(val) if val else None


async def set_ema25(instId: str, value: float):
    r = await get_redis()
    await r.set(f"ema25:{instId}", value)


async def get_ema25(instId: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"ema25:{instId}")
    return float(val) if val else None


async def set_ema50(instId: str, value: float):
    r = await get_redis()
    await r.set(f"ema50:{instId}", value)


async def get_ema50(instId: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"ema50:{instId}")
    return float(val) if val else None


async def set_daily_close(instId: str, value: float):
    r = await get_redis()
    await r.set(f"daily_close:{instId}", value)


async def get_daily_close(instId: str) -> float | None:
    r = await get_redis()
    val = await r.get(f"daily_close:{instId}")
    return float(val) if val else None


async def push_daily_candle(instId: str, candle: dict):
    r = await get_redis()
    key = f"daily_candles:{instId}"
    await r.lpush(key, json.dumps(candle))
    await r.ltrim(key, 0, 19)  # keep last 20 for RSI(14)


async def get_daily_candles(instId: str) -> list[dict]:
    r = await get_redis()
    raw = await r.lrange(f"daily_candles:{instId}", 0, -1)
    return [json.loads(c) for c in raw]


async def set_signal(instId: str, signal: dict):
    r = await get_redis()
    await r.set(f"signal:{instId}", json.dumps(signal))


async def get_signal(instId: str) -> dict | None:
    r = await get_redis()
    val = await r.get(f"signal:{instId}")
    return json.loads(val) if val else None


async def get_all_signals() -> list[dict]:
    r = await get_redis()
    keys = await r.keys("signal:*")
    if not keys:
        return []
    values = await r.mget(*keys)
    return [json.loads(v) for v in values if v]


async def set_symbols(symbols: list[str]):
    r = await get_redis()
    await r.delete("symbols")
    if symbols:
        await r.sadd("symbols", *symbols)


async def get_symbols() -> list[str]:
    r = await get_redis()
    return sorted(await r.smembers("symbols"))


async def set_prev_candle(instId: str, timeframe: str, candle: dict):
    r = await get_redis()
    await r.set(f"prev_candle:{timeframe}:{instId}", json.dumps(candle))


async def get_prev_candle(instId: str, timeframe: str) -> dict | None:
    r = await get_redis()
    val = await r.get(f"prev_candle:{timeframe}:{instId}")
    return json.loads(val) if val else None


async def push_intraday_vol(instId: str, timeframe: str, vol: float):
    r = await get_redis()
    key = f"vol:{timeframe}:{instId}"
    await r.lpush(key, vol)
    await r.ltrim(key, 0, 19)  # keep last 20 bars


async def get_intraday_vols(instId: str, timeframe: str) -> list[float]:
    r = await get_redis()
    raw = await r.lrange(f"vol:{timeframe}:{instId}", 0, -1)
    return [float(v) for v in raw]


async def cache_raw_response(key: str, data: dict | list):
    r = await get_redis()
    await r.set(f"raw:{key}", json.dumps(data), ex=86400)
