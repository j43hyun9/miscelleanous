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

The volume monitoring system has two detection modes:
1. **Absolute Volume Alert**: Triggers when volume exceeds 10M KRW (configurable via `ALERT_VOLUME_KRW`)
2. **Relative Volume Spike**: Triggers when current volume is 2x+ the recent 5-period average (configurable via `VOLUME_INCREASE_THRESHOLD`)

**Key Configuration:**
- `TICKER`: Target cryptocurrency (currently "cro")
- `VOLUME_INCREASE_THRESHOLD`: Multiplier for spike detection (default: 2.0)
- `MIN_VOLUME_THRESHOLD`: Minimum volume for spike analysis (default: 1M KRW)

## Notes

Missing dependencies to resolve:
- Create `alarm_utils.py` with `AlarmPlayer` class
- Add `requirements.txt` with `requests` dependency
- Consider adding logging and configuration file support