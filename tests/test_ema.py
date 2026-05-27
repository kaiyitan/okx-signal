from app.engine.ema import calculate_ema, update_ema


def test_calculate_ema_basic():
    closes = [float(i) for i in range(1, 22)]  # 21 values
    ema = calculate_ema(closes)
    assert ema is not None
    assert ema > 0


def test_calculate_ema_insufficient_data():
    closes = [1.0] * 5
    assert calculate_ema(closes) is None


def test_update_ema_moves_toward_price():
    prev = 100.0
    result = update_ema(prev, 110.0)
    assert 100.0 < result < 110.0


def test_update_ema_stays_when_price_equal():
    result = update_ema(100.0, 100.0)
    assert result == 100.0
