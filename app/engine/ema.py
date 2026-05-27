def calculate_ema(closes: list[float], period: int = 20) -> float | None:
    if len(closes) < period:
        return None
    k = 2 / (period + 1)
    ema = closes[0]
    for price in closes[1:]:
        ema = price * k + ema * (1 - k)
    return ema


def update_ema(prev_ema: float, new_close: float, period: int = 20) -> float:
    k = 2 / (period + 1)
    return new_close * k + prev_ema * (1 - k)
