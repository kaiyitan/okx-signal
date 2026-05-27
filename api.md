# Crypto Swing Signal API

Base URL:

```text
http://localhost:8000
```

数据来源：OKX REST API (`https://www.okx.com/api/v5`) + OKX WebSocket (`wss://ws.okx.com:8443/ws/v5/public`)

---

# Endpoints

## GET /signals

返回当前所有候选币。

### Response

```json
[
  {
    "symbol": "BTC-USDT",
    "signal": "LONG_ENTRY",
    "timeframe": "15m",
    "confidence": 0.84
  }
]
```

---

## GET /signals/{symbol}

查询某个币当前状态。

### Example

```http
GET /signals/BTC-USDT
```

### Response

```json
{
  "symbol": "BTC-USDT",
  "daily_ema20": 68200,
  "daily_close": 68520,
  "pullback_detected": true,
  "bullish_pattern": "hammer",
  "signal": "LONG_ENTRY"
}
```

---

## GET /health

### Response

```json
{
  "status": "ok"
}
```

---

## GET /symbols

返回当前监控的 OKX USDT 现货交易对列表（Top 100 by 24h volume）。

### Response

```json
[
  "BTC-USDT",
  "ETH-USDT",
  "SOL-USDT"
]
```
