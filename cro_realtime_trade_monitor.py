"""
CRO 실시간 체결내역 모니터링 시스템
Coinone WebSocket API를 사용하여 실시간 거래 데이터 수신
"""

import asyncio
import websockets
import json
import time
from datetime import datetime, timedelta
from collections import deque
from alarm_utils import AlarmPlayer

# 설정
TICKER = "CRO"
PRICE_CURRENCY = "KRW"
PRODUCT_CURRENCY = TICKER
ALERT_VOLUME_KRW = 10000000  # 1천만 KRW 이상시 알림
WEBSOCKET_URL = "wss://api.coinone.co.kr/ws"

# 알림 시스템
alarm_player = AlarmPlayer()

# 1분간 체결내역 저장용 큐 (최대 1분간 데이터)
trade_history = deque()

class RealTimeTradeMonitor:
    def __init__(self):
        self.websocket = None
        self.is_connected = False
        self.total_volume_1min = 0
        self.trade_count_1min = 0

    async def connect(self):
        """WebSocket 연결"""
        try:
            print(f"🔄 Coinone WebSocket 연결 중... ({WEBSOCKET_URL})")
            self.websocket = await websockets.connect(WEBSOCKET_URL)
            self.is_connected = True
            print("✅ WebSocket 연결 성공!")
            return True
        except Exception as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            self.is_connected = False
            return False

    async def subscribe_trades(self):
        """거래 데이터 구독"""
        subscribe_message = {
            "requestType": "SUBSCRIBE",
            "body": {
                "channel": "TRADE",
                "topic": {
                    "priceCurrency": PRICE_CURRENCY,
                    "productCurrency": PRODUCT_CURRENCY
                }
            }
        }

        try:
            await self.websocket.send(json.dumps(subscribe_message))
            print(f"📡 {TICKER}/{PRICE_CURRENCY} 체결내역 구독 요청 전송")
        except Exception as e:
            print(f"❌ 구독 요청 실패: {e}")

    def cleanup_old_trades(self, current_time):
        """1분 이전 거래내역 제거"""
        one_minute_ago = current_time - timedelta(minutes=1)

        while trade_history and trade_history[0]['datetime'] < one_minute_ago:
            old_trade = trade_history.popleft()
            self.total_volume_1min -= old_trade['volume_krw']
            self.trade_count_1min -= 1

    def add_trade(self, trade_data):
        """새로운 거래 추가"""
        current_time = datetime.now()

        # 거래량 계산 (가격 * 수량)
        price = float(trade_data.get('price', 0))
        qty = float(trade_data.get('qty', 0))
        volume_krw = price * qty

        trade_record = {
            'datetime': current_time,
            'price': price,
            'qty': qty,
            'volume_krw': volume_krw,
            'timestamp': trade_data.get('timestamp', int(current_time.timestamp() * 1000))
        }

        trade_history.append(trade_record)
        self.total_volume_1min += volume_krw
        self.trade_count_1min += 1

        return trade_record

    def check_volume_alert(self):
        """거래량 알림 체크"""
        if self.total_volume_1min >= ALERT_VOLUME_KRW:
            return True
        return False

    def print_status(self, latest_trade=None):
        """현재 상태 출력"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if latest_trade:
            print(f"[{current_time}] 💰 체결: {latest_trade['price']:,.0f} KRW × {latest_trade['qty']:.4f} = {latest_trade['volume_krw']:,.0f} KRW")

        if self.check_volume_alert():
            print(f"[{current_time}] 🚨 대량 거래 감지! 1분간 누적 거래량: {self.total_volume_1min:,.0f} KRW")
            print(f"                   📊 체결 건수: {self.trade_count_1min}건")
            alarm_player.play_alarm(1, 0)
        else:
            # 주요 상태만 주기적으로 출력 (거래량이 클 때)
            if self.total_volume_1min > 1000000:  # 100만 이상일 때만
                print(f"[{current_time}] 📈 1분 누적: {self.total_volume_1min:,.0f} KRW ({self.trade_count_1min}건)")

    async def handle_message(self, message):
        """WebSocket 메시지 처리"""
        try:
            data = json.loads(message)

            # 거래 데이터 처리
            if data.get('responseType') == 'SUBSCRIBE' and data.get('body', {}).get('channel') == 'TRADE':
                trade_data = data.get('body', {})

                # 새로운 거래 추가
                latest_trade = self.add_trade(trade_data)

                # 오래된 거래 제거
                self.cleanup_old_trades(datetime.now())

                # 상태 출력
                self.print_status(latest_trade)

            elif data.get('responseType') == 'PONG':
                print("🏓 Pong 수신")

        except json.JSONDecodeError:
            print(f"❌ JSON 파싱 실패: {message}")
        except Exception as e:
            print(f"❌ 메시지 처리 오류: {e}")

    async def ping_loop(self):
        """주기적 Ping 전송"""
        while self.is_connected:
            try:
                await asyncio.sleep(30)  # 30초마다
                if self.websocket:
                    ping_message = {"requestType": "PING"}
                    await self.websocket.send(json.dumps(ping_message))
            except Exception as e:
                print(f"❌ Ping 전송 실패: {e}")
                break

    async def listen(self):
        """메시지 수신 루프"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket 연결이 종료되었습니다.")
            self.is_connected = False
        except Exception as e:
            print(f"❌ 메시지 수신 오류: {e}")
            self.is_connected = False

    async def run(self):
        """메인 실행 함수"""
        print(f"🚀 CRO 실시간 체결내역 모니터링 시작")
        print(f"📊 1분간 누적 거래량이 {ALERT_VOLUME_KRW:,} KRW 이상시 알림")
        print("="*60)

        while True:
            try:
                # WebSocket 연결
                if not await self.connect():
                    print("⏳ 5초 후 재연결 시도...")
                    await asyncio.sleep(5)
                    continue

                # 거래 데이터 구독
                await self.subscribe_trades()

                # Ping과 Listen을 동시에 실행
                await asyncio.gather(
                    self.ping_loop(),
                    self.listen()
                )

            except Exception as e:
                print(f"❌ 연결 오류: {e}")
                self.is_connected = False

            print("⏳ 5초 후 재연결 시도...")
            await asyncio.sleep(5)

async def main():
    monitor = RealTimeTradeMonitor()
    await monitor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 프로그램 오류: {e}")