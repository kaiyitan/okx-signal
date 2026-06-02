import logging
from app.engine.ema import update_ema
from app.engine.patterns import Candle, detect_pattern
from app.cache import redis_client

logger = logging.getLogger(__name__)

RSI_PERIOD = 14
RSI_LOW = 40.0
RSI_HIGH = 60.0


def calculate_rsi(daily_candles: list[dict]) -> float | None:
    # daily_candles are newest-first; need oldest-first for RSI
    closes = [float(c["close"]) for c in reversed(daily_candles)]
    if len(closes) < RSI_PERIOD + 1:
        return None
    closes = closes[-(RSI_PERIOD + 1):]
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]
    avg_gain = sum(gains) / RSI_PERIOD
    avg_loss = sum(losses) / RSI_PERIOD
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _confidence(triggers: list[str]) -> float:
    scores = {
        "bullish_engulfing": 0.35,
        "hammer": 0.25,
        "volume_surge": 0.25,
        "rsi_bounce": 0.15,
    }
    return round(min(sum(scores.get(t, 0) for t in triggers), 1.0), 2)


async def process_daily_candle(instId: str, candle: dict):
    daily_close = float(candle["close"])
    await redis_client.set_daily_close(instId, daily_close)
    await redis_client.push_daily_candle(instId, candle)

    for period, getter, setter in [
        (20, redis_client.get_ema20, redis_client.set_ema20),
        (25, redis_client.get_ema25, redis_client.set_ema25),
        (50, redis_client.get_ema50, redis_client.set_ema50),
    ]:
        prev = await getter(instId)
        if prev:
            await setter(instId, update_ema(prev, daily_close, period))


async def process_intraday_candle(instId: str, timeframe: str, candle: dict):
    ema20 = await redis_client.get_ema20(instId)
    ema25 = await redis_client.get_ema25(instId)
    ema50 = await redis_client.get_ema50(instId)
    daily_close = await redis_client.get_daily_close(instId)

    if not all([ema20, ema25, ema50, daily_close]):
        return

    # Condition 1: EMA20 > EMA50 (uptrend)
    if ema20 <= ema50:
        return

    # Condition 2: price pulled back into EMA50–EMA25 zone
    lo, hi = min(ema50, ema25), max(ema50, ema25)
    if not (lo <= daily_close <= hi):
        return

    curr_vol = float(candle.get("vol", 0))
    await redis_client.push_intraday_vol(instId, timeframe, curr_vol)
    avg_vols = await redis_client.get_intraday_vols(instId, timeframe)

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
    curr = Candle(
        open=float(candle["open"]),
        high=float(candle["high"]),
        low=float(candle["low"]),
        close=float(candle["close"]),
        vol=curr_vol,
    )

    patterns = detect_pattern(prev, curr, avg_vols)

    daily_candles = await redis_client.get_daily_candles(instId)
    rsi = calculate_rsi(daily_candles)
    rsi_bounce = rsi is not None and RSI_LOW <= rsi <= RSI_HIGH

    if not patterns and not rsi_bounce:
        return

    triggers = list(patterns)
    if rsi_bounce:
        triggers.append("rsi_bounce")

    signal_type = "confirmed_signal" if candle.get("confirm") == "1" else "preview_signal"
    signal = {
        "symbol": instId,
        "signal": "LONG_ENTRY",
        "signal_type": signal_type,
        "timeframe": timeframe,
        "triggers": triggers,
        "daily_ema20": round(ema20, 4),
        "daily_ema25": round(ema25, 4),
        "daily_ema50": round(ema50, 4),
        "daily_close": round(daily_close, 4),
        "rsi14": rsi,
        "confidence": _confidence(triggers),
    }
    await redis_client.set_signal(instId, signal)
    logger.info(f"Signal {instId} {timeframe} triggers={triggers} conf={signal['confidence']}")

    if candle.get("confirm") == "1":
        await redis_client.set_prev_candle(instId, timeframe, {
            "open": candle["open"],
            "high": candle["high"],
            "low": candle["low"],
            "close": candle["close"],
        })
