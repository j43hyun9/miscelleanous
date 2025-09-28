# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for CRO (Cronos) cryptocurrency volume monitoring and alerting system using the Coinone exchange API. The system detects both absolute volume thresholds and relative volume spikes compared to recent averages.

## Development Commands

- Run the CRO volume monitor: `python cro_volume_monitor.py`
- Check Python syntax: `python -m py_compile cro_volume_monitor.py`
- Format code (if black is available): `black cro_volume_monitor.py`
- Lint code (if pylint is available): `pylint cro_volume_monitor.py`

## Project Structure

The repository currently contains:
- `cro_volume_monitor.py` - CRO volume monitoring script with dual alert system
- `alarm_utils.py` - Missing dependency for alarm functionality

## Coinone API Information

This project uses the Coinone Chart API:
- **Base URL**: https://api.coinone.co.kr/public/v2/chart/{quote_currency}/{target_currency}
- **Purpose**: Retrieve candlestick chart data for cryptocurrency trading pairs
- **Key Parameters**:
  - `interval`: Chart time units (1m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 1w, 1mon)
  - `timestamp`: Last candle's timestamp (UTC Unix time in ms)
  - `size`: Number of candles (1-500, default: 200)
- **Response**: JSON with chart data including timestamp, OHLCV data

## Alert System Features

The volume monitoring system operates with:
- **Check Interval**: Every 10 seconds (configurable via `CHECK_INTERVAL`)
- **Alert Condition**: Triggers when 1-minute summed volume exceeds 10M KRW
- **Data Source**: Primary: 10-second candlestick data (6 candles = 1 minute), Fallback: 1-minute candlestick data
- **Volume Calculation**: Sums 6 consecutive 10-second intervals for precise 1-minute volume
- **Real-time Monitoring**: Continuous monitoring with detailed timestamped logs

**Key Configuration:**
- `TICKER`: Target cryptocurrency (currently "cro")
- `ALERT_VOLUME_KRW`: Volume threshold for alerts (default: 10M KRW)
- `CHECK_INTERVAL`: Check frequency in seconds (default: 10 seconds)
- `URL_10S`: 10-second interval API endpoint
- `URL_1M`: 1-minute interval API endpoint (fallback)

## Usage Example

```bash
python cro_volume_monitor.py
```

**Sample Output (10-second data mode):**
```
🚀 CRO 거래량 모니터링 시작 (10초마다 체크, 10,000,000 KRW 이상 알림)
📊 10초 간격 데이터를 합산하여 1분간 실제 거래량 계산
============================================================
[2024-09-28 14:30:15] ✅ 정상 - 1분 합산: 4,250,000 KRW (평균 10초당: 708,333)
                      🔍 10초별: ['650,000', '720,000', '890,000', '680,000', '800,000', '510,000']
[2024-09-28 14:30:25] 🚨 대량 거래 감지! 1분간 합산 거래량: 12,500,000 KRW
                      📊 10초별 거래량: ['1,200,000', '2,800,000', '3,100,000', '2,200,000', '1,900,000', '1,300,000']
                      📈 평균 10초당: 2,083,333 KRW
```

**Sample Output (1-minute fallback mode):**
```
[2024-09-28 14:30:35] ✅ 정상 - 현재: 3,450,000 KRW, 이전: 2,890,000 KRW
[2024-09-28 14:30:45] 🚨 대량 거래 감지! 현재 1분 거래량: 12,500,000 KRW
                      📊 이전 1분 거래량: 3,450,000 KRW
```

## Notes

- All dependencies are now included (`alarm_utils.py` provided)
- Add `requirements.txt` with `requests` dependency for production use
- Consider adding configuration file support for multiple cryptocurrencies