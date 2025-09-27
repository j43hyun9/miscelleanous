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
- **Alert Condition**: Triggers when current 1-minute volume exceeds 10M KRW
- **Data Source**: Coinone 1-minute candlestick data
- **Real-time Monitoring**: Continuous monitoring with timestamped logs

**Key Configuration:**
- `TICKER`: Target cryptocurrency (currently "cro")
- `ALERT_VOLUME_KRW`: Volume threshold for alerts (default: 10M KRW)
- `CHECK_INTERVAL`: Check frequency in seconds (default: 10 seconds)

## Usage Example

```bash
python cro_volume_monitor.py
```

**Sample Output:**
```
🚀 CRO 거래량 모니터링 시작 (10초마다 체크, 10,000,000 KRW 이상 알림)
============================================================
[2024-09-28 14:30:15] ✅ 정상 - 현재: 3,450,000 KRW, 이전: 2,890,000 KRW
[2024-09-28 14:30:25] 🚨 대량 거래 감지! 현재 1분 거래량: 12,500,000 KRW
                      📊 이전 1분 거래량: 3,450,000 KRW
```

## Notes

- All dependencies are now included (`alarm_utils.py` provided)
- Add `requirements.txt` with `requests` dependency for production use
- Consider adding configuration file support for multiple cryptocurrencies