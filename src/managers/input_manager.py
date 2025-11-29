from typing import TYPE_CHECKING, Set, Dict, List, Optional, Any

from src.settings import mushitroom_config


if TYPE_CHECKING:
    import tkinter as tk
root: "tk.Tk | None" = None


class InputState:
    """현재 프레임의 입력 상태를 저장하는 데이터 클래스"""

    def __init__(self):
        self.up: bool = False
        self.down: bool = False
        self.left: bool = False
        self.right: bool = False
        self.enter: bool = False
        self.prev: bool = False
        self.next: bool = False

        # 현재 눌려있는 키들의 집합 (지속적인 입력 체크용)
        self.pressed_keys: Set[str] = set()
        # 이번 프레임에 막 눌린 키들의 집합 (한 번만 실행되는 트리거용)
        self.just_pressed_keys: Set[str] = set()


class InputManager:
    # tk.Tk 대신 Any를 사용하여 Pylance의 타입 추론 오류(변수 사용 불가) 해결
    def __init__(self, is_windows: bool, root: "tk.Tk | None" = None):
        self.state = InputState()
        self.is_windows = is_windows

        # 키 매핑: 논리적 동작 -> 물리적 키(윈도우용) 리스트
        self.key_map: Dict[str, List[str]] = {
            "up": ["Up", "w"],
            "down": ["Down", "s"],
            "left": ["Left", "a"],
            "right": ["Right", "d"],
            "enter": ["Return"],
            "prev": ["bracketleft", "q"],  # '[' or 'q'
            "next": ["bracketright", "e"],  # ']' or 'e'
        }

        if self.is_windows:
            if root is None:
                print(
                    "경고: Windows 모드지만 root 객체가 전달되지 않았습니다. 키 입력을 받을 수 없습니다."
                )
            else:
                self._setup_windows(root)
        else:
            self._setup_rpi()

    def _setup_windows(self, root: "tk.Tk | None"):
        """Windows Tkinter 키 바인딩 설정"""
        if root is not None:
            root.bind("<KeyPress>", self._on_key_press)
            root.bind("<KeyRelease>", self._on_key_release)

    def _setup_rpi(self):
        """Raspberry Pi GPIO 설정"""
        try:
            from gpiozero import Button

            # TODO: 실제 핀 번호에 맞게 수정 필요
            self.gpio_buttons = {
                "up": Button(17),
                "down": Button(27),
                "left": Button(22),
                "right": Button(23),
                "prev": Button(mushitroom_config.BUTTON_UP),
                "next": Button(mushitroom_config.BUTTON_DOWN),
                "enter": Button(mushitroom_config.BUTTON_RETURN),
            }
        except ImportError:
            print("GPIO 모듈 로드 실패: RPi 환경이 아니거나 라이브러리가 없습니다.")
            self.gpio_buttons = {}

    def _on_key_press(self, event):
        """Tkinter KeyPress 이벤트 콜백"""
        sym = event.keysym
        if sym not in self.state.pressed_keys:
            self.state.just_pressed_keys.add(sym)
        self.state.pressed_keys.add(sym)
        self._update_logical_state(sym, True)

    def _on_key_release(self, event):
        """Tkinter KeyRelease 이벤트 콜백"""
        sym = event.keysym
        if sym in self.state.pressed_keys:
            self.state.pressed_keys.remove(sym)
        self._update_logical_state(sym, False)

    def _update_logical_state(self, sym: str, is_pressed: bool):
        """물리적 키 입력을 논리적 상태(up, down 등)로 매핑"""
        if sym in self.key_map["up"]:
            self.state.up = is_pressed
        if sym in self.key_map["down"]:
            self.state.down = is_pressed
        if sym in self.key_map["left"]:
            self.state.left = is_pressed
        if sym in self.key_map["right"]:
            self.state.right = is_pressed
        if sym in self.key_map["enter"]:
            self.state.enter = is_pressed
        if sym in self.key_map["prev"]:
            self.state.prev = is_pressed
        if sym in self.key_map["next"]:
            self.state.next = is_pressed

    def update(self):
        """
        매 프레임 호출.
        RPi의 경우 여기서 GPIO를 폴링하여 상태를 업데이트합니다.
        """
        if not self.is_windows:
            # RPi GPIO 폴링 로직 예시
            # if "up" in self.gpio_buttons:
            #     self.state.up = self.gpio_buttons["up"].is_pressed
            pass

    def clear_just_pressed(self):
        """프레임 처리가 끝난 후 just_pressed 상태를 초기화"""
        self.state.just_pressed_keys.clear()
