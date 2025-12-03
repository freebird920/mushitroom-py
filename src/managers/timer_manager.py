import time
from typing import Callable, Dict, Any


class TimerManager:
    """
    게임 시간 관리 및 setInterval 기능을 제공하는 싱글톤 클래스
    """

    _instance = None
    _start_time = 0.0
    _is_running = False

    # 타이머 ID 카운터 및 등록된 인터벌들을 저장할 딕셔너리
    # 구조: { id: { 'callback': func, 'interval': float, 'last_time': float } }
    _intervals: Dict[int, Dict[str, Any]] = {}
    _id_counter = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimerManager, cls).__new__(cls)
            cls._instance._intervals = {}
            cls._instance._id_counter = 0
        return cls._instance

    def start(self):
        """타이머 시작"""
        if not self._is_running:
            self._start_time = time.monotonic()
            self._is_running = True
            print("🕒 게임 타이머가 시작되었습니다.")

    def reset(self):
        """타이머 초기화 (등록된 인터벌은 유지됨)"""
        self._start_time = time.monotonic()
        self._is_running = True
        # 인터벌들의 기준 시간도 현재로 리셋하여 튀는 현상 방지
        current = self.get_elapsed_time()
        for t in self._intervals.values():
            t["last_time"] = current
        print("🔄 게임 타이머가 재설정되었습니다.")

    def get_elapsed_time(self) -> float:
        """현재 경과 시간 반환"""
        if not self._is_running:
            return 0.0
        return time.monotonic() - self._start_time

    def stop(self):
        self._is_running = False
        print("🛑 게임 타이머가 정지되었습니다.")

    # --- [추가된 기능] setInterval 구현 ---

    def set_interval(self, callback: Callable, seconds: float) -> int:
        """
        일정 시간(seconds)마다 callback 함수를 실행하도록 등록합니다.
        :param callback: 실행할 함수
        :param seconds: 실행 주기 (초)
        :return: 타이머 ID (나중에 취소할 때 사용)
        """
        timer_id = self._id_counter
        self._id_counter += 1

        self._intervals[timer_id] = {
            "callback": callback,
            "interval": seconds,
            "last_time": self.get_elapsed_time(),  # 등록 시점을 기준으로 시작
        }
        return timer_id

    def clear_interval(self, timer_id: int):
        """등록된 인터벌 타이머를 제거합니다."""
        if timer_id in self._intervals:
            del self._intervals[timer_id]

    def clear_all_intervals(self):
        """모든 인터벌 타이머를 제거합니다. (씬 전환 시 유용)"""
        self._intervals.clear()

    def update(self):
        """
        [중요] 매 프레임(또는 게임 루프)마다 호출되어야 합니다.
        등록된 인터벌들을 확인하고 시간이 되면 콜백을 실행합니다.
        """
        if not self._is_running:
            return

        current_time = self.get_elapsed_time()

        # 딕셔너리를 순회하다가 삭제될 수 있으므로 list로 감싸서 복사본을 순회
        for timer_id, data in list(self._intervals.items()):
            interval = data["interval"]
            last_time = data["last_time"]

            # 시간이 되었는지 확인 (오차 보정 로직 포함)
            # while을 사용하여 프레임 드랍 시 여러 번 실행해야 한다면 여기서 처리
            # (애니메이션의 경우 보통 최신 상태만 보여주면 되므로 if로 처리하거나,
            #  필요 시 while로 변경 가능. 여기선 누적 보정을 위해 if 사용)
            if current_time - last_time >= interval:
                # 콜백 실행
                data["callback"]()

                # 다음 실행 시간 갱신 (오차 누적 방지를 위해 interval만큼 더함)
                # 만약 렉이 심해서 여러 번 건너뛰어야 한다면 아래와 같이 처리:
                while current_time - data["last_time"] >= interval:
                    data["last_time"] += interval
