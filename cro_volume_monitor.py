from datetime import datetime, timedelta
import requests
import time
from alarm_utils import AlarmPlayer

TICKER = "cro"
ALERT_VOLUME_KRW = 10000000  # 1천만 KRW 이상시 알림
CHECK_INTERVAL = 10  # 10초마다 체크

# 1분 간격 데이터를 가져오되, 최근 5분 데이터 조회
URL = f"https://api.coinone.co.kr/public/v2/chart/KRW/{TICKER}?interval=1m&size=5"
alarm_player = AlarmPlayer()

print(f"🚀 CRO 거래량 모니터링 시작 (10초마다 체크, {ALERT_VOLUME_KRW:,} KRW 이상 알림)")
print("="*60)

def check_one_minute_volume(chart_data):
    """
    현재-1분 ~ 현재 사이의 거래량이 1천만 이상인지 체크

    Args:
        chart_data: API에서 받은 차트 데이터 리스트

    Returns:
        tuple: (알림여부, 현재분거래량, 이전분거래량)
    """
    if len(chart_data) < 2:
        return False, 0, 0

    # 최신 1분 거래량 (chart[-1])
    current_minute_volume = float(chart_data[-1]['quote_volume'])

    # 이전 1분 거래량 (chart[-2]) - 참고용
    previous_minute_volume = float(chart_data[-2]['quote_volume'])

    # 현재 1분 거래량이 1천만 KRW 이상이면 알림
    alert_triggered = current_minute_volume >= ALERT_VOLUME_KRW

    return alert_triggered, current_minute_volume, previous_minute_volume

while True:
    try:
        # 현재 시간 출력
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # API 호출
        response = requests.get(URL)
        data = response.json()

        if 'chart' not in data or len(data['chart']) < 1:
            print(f"[{current_time}] ❌ 차트 데이터가 없습니다.")
            time.sleep(CHECK_INTERVAL)
            continue

        # 1분 거래량 체크
        alert_triggered, current_volume, prev_volume = check_one_minute_volume(data['chart'])

        # 결과 출력
        if alert_triggered:
            print(f"[{current_time}] 🚨 대량 거래 감지! 현재 1분 거래량: {current_volume:,.0f} KRW")
            print(f"                   📊 이전 1분 거래량: {prev_volume:,.0f} KRW")
            alarm_player.play_alarm(1, 0)
        else:
            print(f"[{current_time}] ✅ 정상 - 현재: {current_volume:,.0f} KRW, 이전: {prev_volume:,.0f} KRW")

        # 10초 대기
        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{error_time}] ❌ 오류 발생: {e}")
        time.sleep(CHECK_INTERVAL)