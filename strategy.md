# Strategy Definition - Swing Entry Candidate Scanner

# Goal

扫描 Top100 加密货币，识别适合 Swing Trade Long Entry 的候选币。

---

# Universe

仅扫描：

- Top100 市值加密货币
- OKX USDT 现货对（instType=SPOT）

市值排名来源：

- CoinGecko API：`GET https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100`
- 每日刷新一次，取 `symbol` 字段拼接为 OKX instId 格式（如 `BTC-USDT`）
- 过滤掉 OKX 不支持的交易对

例如：

```text
BTC-USDT
ETH-USDT
SOL-USDT
AVAX-USDT
```

---

# Strategy Overview

策略核心：

```text
Daily Trend Filter
+
Daily Pullback
+
Intraday Bullish Confirmation
```

---

# Step 1 - Daily Trend Filter

条件：

```text
daily_close > daily_ema20
```

含义：

- 日线维持上升趋势
- 只做顺势多头

---

# Step 2 - Pullback Detection

最近 3~5 根日线：

```text
low <= ema20 * 1.005
```

即：

- 回踩 Daily EMA20
- 允许 0.5% 误差

目的：

- 避免追高
- 等待健康回调

---

# Step 3 - Intraday Confirmation

周期：

- 15m
- 1h

识别：

- Hammer
- Bullish Engulfing

---

# Hammer Rules

条件：

- Lower wick >= body * 2
- Close near high
- Small candle body

---

# Bullish Engulfing Rules

条件：

- 前一根为 bearish
- 当前 bullish body 完全吞没前一根实体

---

# Candidate Selection

满足以下全部条件：

```text
Daily trend OK
AND
Pullback detected
AND
Bullish candle detected
```

输出：

```json
{
  "symbol": "SOLUSDT",
  "signal": "LONG_ENTRY",
  "confidence": 0.84
}
```

---

# Confidence Score

建议：

| Condition | Weight |
|---|---|
| Above EMA20 | 0.3 |
| Pullback | 0.3 |
| Bullish Pattern | 0.4 |

---

# Signal Types

## preview_signal

未收盘 Kline。

仅用于提前观察。

---

## confirmed_signal

收盘确认。

正式候选。

---

# Scan Frequency

## Daily EMA

每天更新一次。

## Intraday

每秒更新实时价格。

每根 Kline 收盘时确认信号。

---

# Risk Controls

过滤：

- Low volume coins
- Abnormal spread
- Delisted pairs

---

# Future Improvements

- ATR Filter
- Volume Confirmation
- BTC Market Regime
- Multi-timeframe scoring
