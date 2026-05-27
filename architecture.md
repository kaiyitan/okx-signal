# Crypto Swing Signal Service - Architecture

## Overview

本系统用于实时扫描 Top100 市值加密货币，并识别以下 Swing Trade 多头进场条件：

- Daily Close > Daily EMA20
- Daily Pullback toward EMA20
- 15m / 1h Bullish Candle Confirmation
  - Hammer
  - Bullish Engulfing

系统采用：

- OKX WebSocket 实时行情
- FastAPI 查询接口
- Redis 实时缓存
- Docker Compose 部署

---

# High Level Architecture

```text
   CoinGecko API (市值 Top100，每日刷新)
                         |
                         v
                 OKX WebSocket (wss://ws.okx.com:8443/ws/v5/public)
                         |
                         v
               +------------------+
               | Market Worker    |
               | Tick Aggregator  |
               +------------------+
                         |
                         v
               +------------------+
               | Signal Engine    |
               | EMA + Patterns   |
               +------------------+
                         |
                         v
                   +-----------+
                   | Redis     |
                   | 信号/EMA  |
                   | 原始响应  |
                   +-----------+
                         |
                         v
                   +-----------+
                   | FastAPI   |
                   | Query API |
                   +-----------+
```

# Components

## Market Worker
负责：
- 连接 OKX WebSocket (`wss://ws.okx.com:8443/ws/v5/public`)
- 订阅 K线频道：`candle1D` / `candle15m` / `candle1H`
- 聚合实时 Kline
- 更新价格缓存

## Signal Engine
负责：
- Daily EMA20
- Pullback detection
- Bullish candle detection
- Signal generation

## Redis
负责：
- 存储实时信号
- 缓存 EMA
- 缓存每次 OKX / CoinGecko API 调用的原始响应（用于调试和审计）
- 提供快速查询

Key 设计：
```text
signal:{instId}          → 当前信号 JSON
ema20:{instId}           → 当前 Daily EMA20 值
raw:okx:candles:{instId} → OKX K线原始响应
raw:coingecko:top100     → CoinGecko 市值列表原始响应
```

## FastAPI
负责：
- REST API
- Signal 查询
- Health Check

# Deployment

## Stack

- Docker
- Docker Compose
- Ubuntu VPS

## Services

```yaml
api
worker
redis
```

# Future

- Frontend Dashboard
- PostgreSQL Backtesting
