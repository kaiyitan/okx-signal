from dataclasses import dataclass


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float


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


def detect_pattern(prev: Candle | None, curr: Candle) -> str | None:
    if is_hammer(curr):
        return "hammer"
    if prev and is_bullish_engulfing(prev, curr):
        return "bullish_engulfing"
    return None
