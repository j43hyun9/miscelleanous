"""
알람 기능을 제공하는 유틸리티 모듈
"""

import sys
import time

class AlarmPlayer:
    """알람 재생을 위한 클래스"""

    def __init__(self):
        """AlarmPlayer 초기화"""
        self.enabled = True

    def play_alarm(self, duration=1, frequency=0):
        """
        알람을 재생합니다.

        Args:
            duration (int): 알람 지속 시간 (초)
            frequency (int): 주파수 (현재 미사용)
        """
        if not self.enabled:
            return

        print("\n" + "="*50)
        print("🚨 VOLUME ALERT TRIGGERED! 🚨")
        print("="*50)

        # Windows에서 비프음 재생 시도
        try:
            import winsound
            # 비프음 재생 (주파수 1000Hz, 지속시간 1초)
            for _ in range(duration):
                winsound.Beep(1000, 1000)
        except ImportError:
            # winsound가 없는 경우 콘솔 비프음
            try:
                for _ in range(duration * 3):
                    print('\a', end='', flush=True)  # 시스템 비프음
                    time.sleep(0.3)
            except:
                # 모든 것이 실패하면 시각적 알람만
                for i in range(5):
                    print(f"🔔 ALERT #{i+1} 🔔")
                    time.sleep(0.5)

        print("="*50 + "\n")

    def enable(self):
        """알람 활성화"""
        self.enabled = True
        print("🔊 알람이 활성화되었습니다.")

    def disable(self):
        """알람 비활성화"""
        self.enabled = False
        print("🔇 알람이 비활성화되었습니다.")

    def is_enabled(self):
        """알람 활성화 상태 확인"""
        return self.enabled


if __name__ == "__main__":
    # 테스트 코드
    player = AlarmPlayer()
    print("알람 테스트를 시작합니다...")
    player.play_alarm(1, 0)
    print("알람 테스트 완료!")