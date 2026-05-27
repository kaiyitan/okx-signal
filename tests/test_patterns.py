from app.engine.patterns import Candle, is_hammer, is_bullish_engulfing, detect_pattern


def test_hammer_valid():
    # Long lower wick, small body near top
    c = Candle(open=100, high=102, low=90, close=101)
    assert is_hammer(c)


def test_hammer_bearish_candle():
    # Bearish candle should not be hammer
    c = Candle(open=101, high=102, low=90, close=100)
    assert not is_hammer(c)


def test_hammer_small_lower_wick():
    c = Candle(open=100, high=102, low=99, close=101)
    assert not is_hammer(c)


def test_bullish_engulfing_valid():
    prev = Candle(open=105, high=106, low=98, close=99)
    curr = Candle(open=98, high=112, low=97, close=107)
    assert is_bullish_engulfing(prev, curr)


def test_bullish_engulfing_both_bullish():
    prev = Candle(open=98, high=106, low=97, close=105)
    curr = Candle(open=105, high=112, low=104, close=110)
    assert not is_bullish_engulfing(prev, curr)


def test_bullish_engulfing_not_full_engulf():
    prev = Candle(open=105, high=106, low=98, close=99)
    curr = Candle(open=100, high=104, low=99, close=103)
    assert not is_bullish_engulfing(prev, curr)


def test_detect_pattern_returns_hammer():
    curr = Candle(open=100, high=102, low=90, close=101)
    assert detect_pattern(None, curr) == "hammer"


def test_detect_pattern_returns_engulfing():
    prev = Candle(open=105, high=106, low=98, close=99)
    curr = Candle(open=98, high=112, low=97, close=107)
    assert detect_pattern(prev, curr) == "bullish_engulfing"


def test_detect_pattern_returns_none():
    curr = Candle(open=100, high=101, low=99, close=100.5)
    assert detect_pattern(None, curr) is None
