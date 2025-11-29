from typing import TYPE_CHECKING, Set, Dict, List, Optional
from src.settings.mushitroom_enums import InputActions
from src.settings import mushitroom_config

if TYPE_CHECKING:
    import tkinter as tk


class InputState:
    """현재 프레임의 입력 상태를 저장하는 데이터 클래스 (Set 기반 리팩토링)"""

    def __init__(self):
        # [변경] 개별 bool 변수 제거 -> 눌려있는 액션들의 집합 (Hold)
        # 예: {InputActions.UP, InputActions.ENTER}
        self.held_actions: Set[InputActions] = set()

        # [변경] 이번 프레임에 막 눌린 액션들의 집합 (Trigger)
        self.just_pressed_actions: Set[InputActions] = set()

        # 물리적 키 상태 (디버깅용 혹은 로우 레벨 처리용)
        self.pressed_keys: Set[str] = set()

    def is_held(self, action: InputActions) -> bool:
        """해당 액션 키를 누르고 있는가?"""
        return action in self.held_actions

    def is_just_pressed(self, action: InputActions) -> bool:
        """해당 액션 키를 방금 눌렀는가?"""
        return action in self.just_pressed_actions

    def clear_just_pressed(self):
        """프레임 종료 후 트리거 초기화"""
        self.just_pressed_actions.clear()
        # pressed_keys의 just_pressed 로직이 필요 없다면 제거해도 됩니다.


class InputManager:
    def __init__(self, is_windows: bool, root: "tk.Tk | None" = None):
        self.state = InputState()
        self.is_windows = is_windows

        # 키 매핑: 논리적 동작 -> 물리적 키 리스트
        self.key_map: Dict[InputActions, List[str]] = {
            InputActions.UP: ["Up"],
            InputActions.DOWN: ["Down"],
            InputActions.LEFT: ["Left"],
            InputActions.RIGHT: ["Right"],
            InputActions.ENTER: ["Return", "space"],
            InputActions.PREV: ["bracketleft", "q", "Left"],
            InputActions.NEXT: ["bracketright", "e", "Right"],
        }

        # 역방향 매핑 생성 (물리적 키 -> 논리적 동작)
        self._key_to_action: Dict[str, InputActions] = {}
        for action, keys in self.key_map.items():
            for key in keys:
                self._key_to_action[key] = action

        if self.is_windows:
            if root:
                self._setup_windows(root)
        else:
            self._setup_rpi()

    def _setup_windows(self, root: "tk.Tk"):
        root.bind("<KeyPress>", self._on_key_press)
        root.bind("<KeyRelease>", self._on_key_release)

    def _setup_rpi(self):
        try:
            from gpiozero import Button

            # GPIO 버튼 설정
            self.gpio_buttons: Dict[InputActions, Button] = {
                InputActions.PREV: Button(
                    mushitroom_config.GPIO_PINS.BUTTON_UP,
                    pull_up=True,
                    bounce_time=mushitroom_config.BUTTON_BOUNCE_TIME,
                ),
                InputActions.NEXT: Button(
                    mushitroom_config.GPIO_PINS.BUTTON_DOWN,
                    pull_up=True,
                    bounce_time=mushitroom_config.BUTTON_BOUNCE_TIME,
                ),
                InputActions.ENTER: Button(
                    mushitroom_config.GPIO_PINS.BUTTON_RETURN,
                    pull_up=True,
                    bounce_time=mushitroom_config.BUTTON_BOUNCE_TIME,
                ),
            }

            # 람다 대신 부분 적용이나 클로저를 명확히 사용하여 바인딩
            for action, btn in self.gpio_buttons.items():
                # GPIOZero는 press/release 이벤트를 제공함
                btn.when_pressed = lambda a=action: self._on_gpio_press(a)
                btn.when_released = lambda a=action: self._on_gpio_release(a)

        except ImportError:
            print("GPIO 모듈 로드 실패: RPi 환경이 아니거나 라이브러리가 없습니다.")
            self.gpio_buttons = {}

    def _on_key_press(self, event):
        sym = event.keysym

        # 물리 키 기록 (필요하다면 유지)
        if sym not in self.state.pressed_keys:
            # 여기서는 물리 키 just_pressed 로직은 생략했습니다. 필요하면 추가 가능.
            pass
        self.state.pressed_keys.add(sym)

        # 논리 액션 처리
        action = self._key_to_action.get(sym)
        if action:
            # [변경] 기존에는 bool 체크였으나, 이제 set 체크로 변경
            if action not in self.state.held_actions:
                self.state.just_pressed_actions.add(action)

            self.state.held_actions.add(action)

    def _on_key_release(self, event):
        sym = event.keysym
        if sym in self.state.pressed_keys:
            self.state.pressed_keys.remove(sym)

        action = self._key_to_action.get(sym)
        if action:
            # [변경] set에서 제거 (discard는 없어도 에러 안 남)
            self.state.held_actions.discard(action)

    def _on_gpio_press(self, action: InputActions):
        # [변경] GPIO 로직도 set 기반으로 단순화
        if action not in self.state.held_actions:
            self.state.just_pressed_actions.add(action)

        self.state.held_actions.add(action)

    def _on_gpio_release(self, action: InputActions):
        # [변경] set에서 제거
        self.state.held_actions.discard(action)

    def clear_just_pressed(self):
        """게임 루프의 끝에서 호출하여 트리거 상태 초기화"""
        self.state.clear_just_pressed()
