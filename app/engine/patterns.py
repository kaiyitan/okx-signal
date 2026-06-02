from dataclasses import dataclass, field


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    vol: float = field(default=0.0)


def is_hammer(c: Candle) -> bool:
    body = abs(c.close - c.open)
    if body == 0:
        body = (c.high - c.low) * 0.001
    lower_wick = min(c.open, c.close) - c.low
    upper_wick = c.high - max(c.open, c.close)
    return (
        c.close > c.open
        and lower_wick >= body * 2
        and upper_wick <= body * 0.5
    )


def is_bullish_engulfing(prev: Candle, curr: Candle) -> bool:
    prev_bearish = prev.close < prev.open
    curr_bullish = curr.close > curr.open
    if not (prev_bearish and curr_bullish):
        return False
    return curr.open <= prev.close and curr.close >= prev.open


def is_volume_surge(curr: Candle, avg_vols: list[float]) -> bool:
    if not avg_vols or curr.vol == 0:
        return False
    avg = sum(avg_vols) / len(avg_vols)
    return avg > 0 and curr.vol > avg * 1.5 and curr.close > curr.open


def detect_pattern(
    prev: Candle | None,
    curr: Candle,
    avg_vols: list[float] | None = None,
) -> list[str]:
    patterns = []
    if is_hammer(curr):
        patterns.append("hammer")
    if prev and is_bullish_engulfing(prev, curr):
        patterns.append("bullish_engulfing")
    if avg_vols and is_volume_surge(curr, avg_vols):
        patterns.append("volume_surge")
    return patterns
