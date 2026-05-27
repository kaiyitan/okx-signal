# Crypto Swing Service - Code Style Guide

# Principles

- Simple
- Readable
- Predictable
- Maintainable

避免：
- Over engineering
- Premature optimization

---

# Python Version

```text
Python 3.11+
```

---

# Formatting

使用：
- black
- isort

---

# Naming

## Variables

```python
daily_ema20
signal_score
pullback_detected
```

## Functions

```python
calculate_daily_ema()
detect_hammer()
generate_signal()
```

## Classes

```python
SignalEngine
MarketWorker
```

---

# Logging

统一使用：

```python
import logging
```

不要：

```python
print()
```

---

# Config

所有配置放入：

```env
OKX_WS_URL=wss://ws.okx.com:8443/ws/v5/public
OKX_REST_URL=https://www.okx.com
COINGECKO_API_URL=https://api.coingecko.com/api/v3
REDIS_HOST=
REDIS_PORT=
CACHE_RAW_RESPONSE=true
```

> 行情为公开接口，无需 OKX API Key。
> `CACHE_RAW_RESPONSE=true` 时，每次 API 调用结果写入 Redis。

---

# Async

推荐：

```python
async/await
```

避免：

```python
time.sleep()
```

---

# Testing

推荐：

```text
pytest
```

重点测试：
- EMA
- Hammer
- Bullish engulfing
