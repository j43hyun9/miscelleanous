from datetime import datetime, timedelta
import requests
import time
from alarm_utils import AlarmPlayer

TICKER = "cro"
ALERT_VOLUME_KRW = 10000000  # 1천만 KRW 이상시 알림
CHECK_INTERVAL = 10  # 10초마다 체크

# 10초 간격 데이터를 가져와서 1분간(6개) 데이터 합산
URL_10S = f"https://api.coinone.co.kr/public/v2/chart/KRW/{TICKER}?interval=10s&size=20"
# 백업용: 1분 간격 데이터
URL_1M = f"https://api.coinone.co.kr/public/v2/chart/KRW/{TICKER}?interval=1m&size=5"

alarm_player = AlarmPlayer()

print(f"🚀 CRO 거래량 모니터링 시작 (10초마다 체크, {ALERT_VOLUME_KRW:,} KRW 이상 알림)")
print("📊 10초 간격 데이터를 합산하여 1분간 실제 거래량 계산")
print("="*60)

def calculate_one_minute_volume_from_10s_data(chart_data_10s):
    """
    10초 간격 데이터에서 최근 1분간(6개) 거래량 합산

    Args:
        chart_data_10s: 10초 간격 차트 데이터 리스트

    Returns:
        tuple: (알림여부, 1분합산거래량, 개별10초거래량리스트)
    """
    if len(chart_data_10s) < 6:
        return False, 0, []

    # 최근 6개 (1분간) 10초 캔들 데이터
    recent_6_candles = chart_data_10s[-6:]

    # 각 10초 구간의 거래량을 합산
    individual_volumes = []
    total_volume = 0

    for candle in recent_6_candles:
        volume = float(candle['quote_volume'])
        individual_volumes.append(volume)
        total_volume += volume

    # 1분간 합산 거래량이 1천만 KRW 이상이면 알림
    alert_triggered = total_volume >= ALERT_VOLUME_KRW

    return alert_triggered, total_volume, individual_volumes

def get_volume_data():
    """거래량 데이터를 가져오는 함수 (10초 간격 우선, 실패시 1분 간격)"""
    try:
        # 10초 간격 데이터 시도
        response = requests.get(URL_10S, timeout=5)
        data = response.json()

        if 'chart' in data and len(data['chart']) >= 6:
            return data['chart'], '10s'

        # 10초 데이터가 부족하면 1분 데이터 사용
        response = requests.get(URL_1M, timeout=5)
        data = response.json()

        if 'chart' in data and len(data['chart']) >= 2:
            return data['chart'], '1m'

        return None, None

    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None, None

while True:
    try:
        # 현재 시간 출력
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 거래량 데이터 가져오기
        chart_data, interval_type = get_volume_data()

        if chart_data is None:
            print(f"[{current_time}] ❌ 차트 데이터를 가져올 수 없습니다.")
            time.sleep(CHECK_INTERVAL)
            continue

        if interval_type == '10s':
            # 10초 간격 데이터에서 1분간 합산
            alert_triggered, total_volume, individual_volumes = calculate_one_minute_volume_from_10s_data(chart_data)

            # 결과 출력
            if alert_triggered:
                print(f"[{current_time}] 🚨 대량 거래 감지! 1분간 합산 거래량: {total_volume:,.0f} KRW")
                print(f"                   📊 10초별 거래량: {[f'{v:,.0f}' for v in individual_volumes]}")
                print(f"                   📈 평균 10초당: {total_volume/6:,.0f} KRW")
                alarm_player.play_alarm(1, 0)
            else:
                avg_per_10s = total_volume / 6
                print(f"[{current_time}] ✅ 정상 - 1분 합산: {total_volume:,.0f} KRW (평균 10초당: {avg_per_10s:,.0f})")
                # 상세 10초별 거래량 표시 (값이 클 때만)
                max_volume = max(individual_volumes) if individual_volumes else 0
                if max_volume > 1000000:  # 100만 이상인 10초 구간이 있으면 표시
                    print(f"                   🔍 10초별: {[f'{v:,.0f}' for v in individual_volumes]}")

        else:  # 1분 간격 데이터 사용
            if len(chart_data) >= 2:
                current_volume = float(chart_data[-1]['quote_volume'])
                prev_volume = float(chart_data[-2]['quote_volume'])
                alert_triggered = current_volume >= ALERT_VOLUME_KRW

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