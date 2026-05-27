import logging
from app.engine.ema import update_ema
from app.engine.patterns import Candle, detect_pattern
from app.cache import redis_client

logger = logging.getLogger(__name__)

PULLBACK_TOLERANCE = 1.005


def _detect_pullback(daily_candles: list[dict], ema20: float) -> bool:
    for c in daily_candles[:5]:
        if float(c["low"]) <= ema20 * PULLBACK_TOLERANCE:
            return True
    return False


def _confidence(above_ema: bool, pullback: bool, pattern: str | None) -> float:
    score = 0.0
    if above_ema:
        score += 0.3
    if pullback:
        score += 0.3
    if pattern:
        score += 0.4
    return round(score, 2)


async def process_daily_candle(instId: str, candle: dict):
    daily_close = float(candle["close"])
    await redis_client.set_daily_close(instId, daily_close)
    await redis_client.push_daily_candle(instId, candle)

    prev_ema = await redis_client.get_ema20(instId)
    if prev_ema:
        new_ema = update_ema(prev_ema, daily_close)
        await redis_client.set_ema20(instId, new_ema)


async def process_intraday_candle(instId: str, timeframe: str, candle: dict):
    ema20 = await redis_client.get_ema20(instId)
    daily_close = await redis_client.get_daily_close(instId)
    if not ema20 or not daily_close:
        return

    above_ema = daily_close > ema20
    if not above_ema:
        return

    daily_candles = await redis_client.get_daily_candles(instId)
    pullback = _detect_pullback(daily_candles, ema20)
    if not pullback:
        return

    curr = Candle(
        open=float(candle["open"]),
        high=float(candle["high"]),
        low=float(candle["low"]),
        close=float(candle["close"]),
    )
    prev_raw = await redis_client.get_prev_candle(instId, timeframe)
    prev = (
        Candle(
            open=float(prev_raw["open"]),
            high=float(prev_raw["high"]),
            low=float(prev_raw["low"]),
            close=float(prev_raw["close"]),
        )
        if prev_raw
        else None
    )

    pattern = detect_pattern(prev, curr)
    signal_type = "confirmed_signal" if candle.get("confirm") == "1" else "preview_signal"

    if pattern:
        signal = {
            "symbol": instId,
            "signal": "LONG_ENTRY",
            "signal_type": signal_type,
            "timeframe": timeframe,
            "bullish_pattern": pattern,
            "daily_ema20": round(ema20, 4),
            "daily_close": round(daily_close, 4),
            "pullback_detected": True,
            "confidence": _confidence(above_ema, pullback, pattern),
        }
        await redis_client.set_signal(instId, signal)
        logger.info(f"Signal {instId} {timeframe} {pattern} conf={signal['confidence']}")

    if candle.get("confirm") == "1":
        await redis_client.set_prev_candle(instId, timeframe, {
            "open": candle["open"],
            "high": candle["high"],
            "low": candle["low"],
            "close": candle["close"],
        })
