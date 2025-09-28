# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for CRO (Cronos) cryptocurrency volume monitoring and alerting system using the Coinone exchange API. The system detects both absolute volume thresholds and relative volume spikes compared to recent averages.

## Development Commands

**Setup:**
```bash
pip install -r requirements.txt
```

**Run monitoring systems:**
```bash
# Candlestick-based monitoring (10-second aggregation)
python cro_volume_monitor.py

# Real-time trade monitoring (WebSocket)
python cro_realtime_trade_monitor.py
```

**Development tools:**
```bash
python -m py_compile *.py          # Syntax check
black *.py                         # Code formatting
pylint *.py                        # Code linting
```

## Project Structure

The repository currently contains:
- `cro_volume_monitor.py` - CRO volume monitoring script using candlestick data aggregation
- `cro_realtime_trade_monitor.py` - Real-time trade monitoring using WebSocket API
- `alarm_utils.py` - Alarm functionality for volume alerts
- `requirements.txt` - Python dependencies

## Coinone API Information

This project uses two Coinone APIs:

### Chart API (REST)
- **Base URL**: https://api.coinone.co.kr/public/v2/chart/{quote_currency}/{target_currency}
- **Purpose**: Retrieve candlestick chart data for cryptocurrency trading pairs
- **Key Parameters**:
  - `interval`: Chart time units (10s, 1m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 1w, 1mon)
  - `timestamp`: Last candle's timestamp (UTC Unix time in ms)
  - `size`: Number of candles (1-500, default: 200)
- **Response**: JSON with chart data including timestamp, OHLCV data

### WebSocket API (Real-time)
- **Base URL**: wss://api.coinone.co.kr/ws
- **Purpose**: Real-time trade execution data
- **Subscription**: TRADE channel for specific trading pairs
- **Response**: Individual trade executions with price, quantity, timestamp

## Alert System Features

Two monitoring approaches available:

### 1. Candlestick-based Monitoring (`cro_volume_monitor.py`)
- **Check Interval**: Every 10 seconds
- **Alert Condition**: Triggers when 1-minute summed volume exceeds 10M KRW
- **Data Source**: Primary: 10-second candlestick data (6 candles = 1 minute), Fallback: 1-minute candlestick data
- **Volume Calculation**: Sums 6 consecutive 10-second intervals for precise 1-minute volume

### 2. Real-time Trade Monitoring (`cro_realtime_trade_monitor.py`)
- **Connection**: WebSocket for real-time trade execution data
- **Alert Condition**: Triggers when 1-minute accumulated trade volume exceeds 10M KRW
- **Data Source**: Individual trade executions (price × quantity)
- **Volume Calculation**: Real-time accumulation of actual trade volumes
- **Auto-cleanup**: Removes trades older than 1 minute

**Key Configuration (both systems):**
- `TICKER`: Target cryptocurrency (currently "cro")
- `ALERT_VOLUME_KRW`: Volume threshold for alerts (default: 10M KRW)
- `WEBSOCKET_URL`: WebSocket endpoint for real-time data

## Usage Examples

### Candlestick-based Monitoring
```bash
python cro_volume_monitor.py
```

**Sample Output:**
```
🚀 CRO 거래량 모니터링 시작 (10초마다 체크, 10,000,000 KRW 이상 알림)
📊 10초 간격 데이터를 합산하여 1분간 실제 거래량 계산
============================================================
[2024-09-28 14:30:15] ✅ 정상 - 1분 합산: 4,250,000 KRW (평균 10초당: 708,333)
                      🔍 10초별: ['650,000', '720,000', '890,000', '680,000', '800,000', '510,000']
[2024-09-28 14:30:25] 🚨 대량 거래 감지! 1분간 합산 거래량: 12,500,000 KRW
                      📊 10초별 거래량: ['1,200,000', '2,800,000', '3,100,000', '2,200,000', '1,900,000', '1,300,000']
```

### Real-time Trade Monitoring
```bash
python cro_realtime_trade_monitor.py
```

**Sample Output:**
```
🚀 CRO 실시간 체결내역 모니터링 시작
📊 1분간 누적 거래량이 10,000,000 KRW 이상시 알림
============================================================
✅ WebSocket 연결 성공!
📡 CRO/KRW 체결내역 구독 요청 전송
[2024-09-28 14:30:15] 💰 체결: 150 KRW × 1000.0000 = 150,000 KRW
[2024-09-28 14:30:16] 💰 체결: 151 KRW × 2500.0000 = 377,500 KRW
[2024-09-28 14:30:17] 📈 1분 누적: 2,450,000 KRW (15건)
[2024-09-28 14:30:45] 🚨 대량 거래 감지! 1분간 누적 거래량: 12,500,000 KRW
                      📊 체결 건수: 127건
```

## Notes

**Dependencies:**
- All required modules included (`alarm_utils.py`, `requirements.txt`)
- Install dependencies: `pip install -r requirements.txt`

**Monitoring Approaches:**
- **Candlestick method**: More stable, aggregated data, good for historical analysis
- **Real-time method**: Most accurate, individual trade executions, best for immediate detection

**Recommendations:**
- Use real-time monitoring for critical volume detection
- Use candlestick monitoring for stable, continuous operation
- Consider running both systems simultaneously for redundancy