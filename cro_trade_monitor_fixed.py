"""
CRO 실시간 체결 모니터링 (누락 방지 개선 버전)
- 같은 분 내 체결 변화량도 모두 감지
- 체결 누락 없이 모든 거래량 변화 추적
"""

import asyncio
import aiohttp
import json
import sys
import io
from datetime import datetime, timedelta
from collections import deque
from alarm_utils import AlarmPlayer

# Windows 환경에서 한글/이모지 출력 문제 해결
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 설정
TICKER = "CRO"
ALERT_VOLUME_KRW = 10000000  # 1천만 KRW 알람 임계값
REST_API_URL = "https://api.coinone.co.kr/public/v2/chart/KRW/CRO"
CHECK_INTERVAL_MS = 100  # 100밀리초마다 체크

# 알림 시스템
alarm_player = AlarmPlayer()

# 1분간 체결내역 저장용
trade_history = deque()

class CROTradeMonitorFixed:
    def __init__(self):
        self.session = None
        self.total_volume_1min = 0  # 1분간 누적 체결액
        self.trade_count_1min = 0   # 1분간 체결 건수
        self.alert_triggered = False  # 중복 알림 방지
        self.last_candle_data = None  # 이전 캔들 데이터 저장

    async def create_session(self):
        """HTTP 세션 생성"""
        self.session = aiohttp.ClientSession()
        print("✅ 모니터링 시작 (누락 방지 개선 버전)")

    async def cleanup_old_trades(self, current_time):
        """1분 이전 거래내역 제거 (슬라이딩 윈도우)"""
        one_minute_ago = current_time - timedelta(minutes=1)

        removed_count = 0
        removed_volume = 0

        while trade_history and trade_history[0]['datetime'] <= one_minute_ago:
            old_trade = trade_history.popleft()
            self.total_volume_1min -= old_trade['volume_krw']
            self.trade_count_1min -= 1
            removed_count += 1
            removed_volume += old_trade['volume_krw']

        # 디버깅용 출력 (제거된 거래가 있을 때만)
        if removed_count > 0:
            current_time_str = current_time.strftime("%H:%M:%S")
            print(f"🧹 [{current_time_str}] 1분 경과 거래 제거: {removed_count}건, {int(removed_volume):,} KRW | 현재 누적: {int(self.total_volume_1min):,} KRW", flush=True)

        # 거래량이 임계값 이하로 떨어지면 알림 상태 리셋
        if self.total_volume_1min < ALERT_VOLUME_KRW and self.alert_triggered:
            self.alert_triggered = False
            current_time_str = current_time.strftime("%H:%M:%S")
            print(f"🔄 [{current_time_str}] 알림 상태 리셋 (누적 거래량 임계값 이하)", flush=True)

    def detect_volume_change(self, current_candle, current_time):
        """거래량 변화 감지 (누락 방지)"""
        if self.last_candle_data is None:
            # 첫 번째 데이터
            self.last_candle_data = current_candle
            current_volume = float(current_candle.get('quote_volume', 0))
            if current_volume > 0:
                return self.create_trade_record(current_candle, current_volume, current_time)
            return None

        # 이전 데이터와 비교
        prev_volume = float(self.last_candle_data.get('quote_volume', 0))
        current_volume = float(current_candle.get('quote_volume', 0))
        prev_timestamp = int(self.last_candle_data.get('timestamp', 0))
        current_timestamp = int(current_candle.get('timestamp', 0))

        volume_change = current_volume - prev_volume

        # 새로운 체결 감지 조건
        new_trade_detected = False
        trade_volume = 0

        if current_timestamp > prev_timestamp:
            # 새로운 분이 시작됨 - 전체 거래량이 새로운 체결
            if current_volume > 0:
                new_trade_detected = True
                trade_volume = current_volume
        elif current_timestamp == prev_timestamp and volume_change > 0:
            # 같은 분 내에서 거래량 증가 - 증가분이 새로운 체결
            new_trade_detected = True
            trade_volume = volume_change

        if new_trade_detected:
            self.last_candle_data = current_candle
            return self.create_trade_record(current_candle, trade_volume, current_time)

        return None

    def create_trade_record(self, candle_data, trade_volume, current_time):
        """체결 기록 생성"""
        close_price = float(candle_data.get('close', 0))
        timestamp = int(candle_data.get('timestamp', 0))

        trade_record = {
            'datetime': current_time,
            'price': close_price,
            'volume_krw': trade_volume,
            'timestamp': timestamp
        }

        # 1분간 데이터에 추가
        trade_history.append(trade_record)
        self.total_volume_1min += trade_volume
        self.trade_count_1min += 1

        return trade_record

    def check_volume_alert(self):
        """1천만원 초과 체크"""
        return self.total_volume_1min >= ALERT_VOLUME_KRW

    def print_trade_and_check_alert(self, latest_trade):
        """체결 출력 및 알람 체크"""
        current_time = datetime.now()

        if latest_trade:
            # 체결시간, 체결가, 체결액, 1분누적 출력
            execution_time_str = current_time.strftime("%H:%M:%S")
            print(f"체결시간: {execution_time_str}, 체결가: {int(float(latest_trade['price'])):,} KRW, 체결액: {int(float(latest_trade['volume_krw'])):,} KRW, 1분누적: {int(self.total_volume_1min):,} KRW", flush=True)

            # 현재시간으로부터 1분전까지 누적 체결액이 1천만원 초과시 알람
            if self.check_volume_alert() and not self.alert_triggered:
                self.alert_triggered = True
                print(f"🚨 [{execution_time_str}] 알람! 1분간 누적 체결액: {int(self.total_volume_1min):,} KRW", flush=True)
                print(f"📊 체결 건수: {self.trade_count_1min}건 | 🎯 임계값: {ALERT_VOLUME_KRW:,} KRW 초과!", flush=True)
                print("="*80, flush=True)
                alarm_player.play_alarm(1, 0)

    async def fetch_latest_data(self):
        """최신 캔들 데이터 가져오기"""
        try:
            params = {
                'interval': '1m',  # 1분 간격
                'size': 1  # 최신 1개만
            }

            async with self.session.get(REST_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('error_code') == '0' and data.get('result') == 'success':
                        chart_data = data.get('chart', [])
                        if chart_data:
                            return chart_data[0]
                else:
                    print(f"❌ API 호출 실패: HTTP {response.status}")

        except Exception as e:
            print(f"❌ 데이터 가져오기 실패: {e}")

        return None

    async def run(self):
        """메인 실행"""
        print(f"🚀 CRO 실시간 체결 모니터링 (누락 방지 개선)")
        print(f"💰 체결시간, 체결가, 체결액, 1분누적 (같은 분 내 변화도 감지)")
        print(f"🚨 1분간 누적 체결액 {ALERT_VOLUME_KRW:,} KRW 초과시 알람")
        print("="*80)

        await self.create_session()

        try:
            while True:
                current_time = datetime.now()

                # 최신 데이터 가져오기
                latest_candle = await self.fetch_latest_data()

                if latest_candle:
                    # 거래량 변화 감지 (누락 방지)
                    latest_trade = self.detect_volume_change(latest_candle, current_time)

                    # 1분 이전 데이터 정리
                    await self.cleanup_old_trades(current_time)

                    # 체결 출력 및 알람 체크
                    if latest_trade:
                        self.print_trade_and_check_alert(latest_trade)

                # 100ms 대기
                await asyncio.sleep(CHECK_INTERVAL_MS / 1000.0)

        except KeyboardInterrupt:
            print("\n👋 모니터링 종료")
        except Exception as e:
            print(f"❌ 오류: {e}")
        finally:
            if self.session:
                await self.session.close()

async def main():
    monitor = CROTradeMonitorFixed()
    await monitor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램 종료")
    except Exception as e:
        print(f"❌ 프로그램 오류: {e}")