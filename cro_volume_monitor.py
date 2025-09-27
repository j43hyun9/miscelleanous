from datetime import datetime, timedelta
import requests
import time
from alarm_utils import AlarmPlayer

TICKER = "cro"
ALERT_VOLUME_KRW = 10000000
VOLUME_INCREASE_THRESHOLD = 2.0  # 2배 이상 증가시 알람
MIN_VOLUME_THRESHOLD = 1000000   # 최소 거래량 (100만 KRW) 이상일 때만 비교

URL = f"https://api.coinone.co.kr/public/v2/chart/KRW/{TICKER}?interval=1m&size=10"
alarm_player = AlarmPlayer()

# 이전 거래량들을 저장할 리스트 (최근 5개 구간 평균과 비교)
previous_volumes = []


# 다음 분의 01초까지 대기
now = datetime.now()
next_minute = (now + timedelta(minutes=1)).replace(second=1, microsecond=0)
time.sleep((next_minute - now).total_seconds())

def check_volume_spike(current_volume, previous_volumes):
    """거래량 급증 여부를 체크하는 함수"""
    if len(previous_volumes) < 3:  # 최소 3개 데이터 필요
        return False, 0

    # 최근 3-5개 구간의 평균 거래량 계산
    recent_avg = sum(previous_volumes[-5:]) / len(previous_volumes[-5:])

    # 현재 거래량이 최소 임계값 이상이고, 평균 대비 일정 배수 이상일 때
    if current_volume >= MIN_VOLUME_THRESHOLD and recent_avg > 0:
        increase_ratio = current_volume / recent_avg
        if increase_ratio >= VOLUME_INCREASE_THRESHOLD:
            return True, increase_ratio

    return False, current_volume / recent_avg if recent_avg > 0 else 0

while True:
  try:
    response = requests.get(URL)
    data = response.json()

    if 'chart' not in data or len(data['chart']) < 2:
        print("차트 데이터가 충분하지 않습니다.")
        time.sleep(60)
        continue

    # 최신 거래량 (인덱스 -1)과 이전 거래량 (인덱스 -2) 가져오기
    current_volume = float(data['chart'][-1]['quote_volume'])
    prev_volume = float(data['chart'][-2]['quote_volume'])

    # 이전 거래량을 리스트에 추가 (최대 10개까지 보관)
    previous_volumes.append(prev_volume)
    if len(previous_volumes) > 10:
        previous_volumes.pop(0)

    print(f"현재 거래량: {current_volume:,.0f} KRW")

    # 기존 절대값 체크
    absolute_alert = current_volume > ALERT_VOLUME_KRW

    # 거래량 급증 체크
    spike_detected, ratio = check_volume_spike(current_volume, previous_volumes)

    if absolute_alert or spike_detected:
        if absolute_alert:
            print(f"🚨 절대 거래량 초과: {current_volume:,.0f} KRW")
        if spike_detected:
            avg_volume = sum(previous_volumes[-5:]) / len(previous_volumes[-5:])
            print(f"📈 거래량 급증 감지: {ratio:.1f}배 증가 (평균: {avg_volume:,.0f} → 현재: {current_volume:,.0f})")

        alarm_player.play_alarm(1, 0)
    else:
        if len(previous_volumes) >= 3:
            avg_volume = sum(previous_volumes[-5:]) / len(previous_volumes[-5:])
            current_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            print(f"거래량 비율: {current_ratio:.1f}배 (평균 대비)")

    time.sleep(60)
  except Exception as e:
    print(f"오류 발생: {e}")
    time.sleep(60)