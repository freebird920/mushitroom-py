from typing import TYPE_CHECKING, Set, Dict, List, Optional
from settings.mushitroom_enums import InputActions
from settings import mushitroom_config

if TYPE_CHECKING:
    import tkinter as tk


class InputState:
    """현재 프레임의 입력 상태를 저장하는 데이터 클래스"""

    def __init__(self):
        self.held_actions: Set[InputActions] = set()
        self.just_pressed_actions: Set[InputActions] = set()
        self.pressed_keys: Set[str] = set()

    def is_held(self, action: InputActions) -> bool:
        return action in self.held_actions

    def is_just_pressed(self, action: InputActions) -> bool:
        return action in self.just_pressed_actions

    def clear_just_pressed(self):
        self.just_pressed_actions.clear()


class InputManager:
    _instance: Optional["InputManager"] = None
    state: InputState
    initialized: bool

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_windows: bool = True, root: "tk.Tk | None" = None):
        if hasattr(self, "initialized") and self.initialized:
            return

        if not hasattr(self, "state"):
            self.state = InputState()
            self.is_windows = is_windows
            self._setup_key_maps()  # 키 매핑 설정 분리

        # [핵심 변경] 플랫폼 설정 시도
        if self.is_windows:
            if root:
                # root가 들어왔을 때만 진짜 세팅하고 '초기화 완료' 도장을 찍음
                self._setup_windows(root)
                print("[System] InputManager 초기화 완료 (Windows)")
                self.initialized = True
            else:
                # root가 없으면? 그냥 넘어감 (initialized=True를 안 함!)
                # 이렇게 하면 나중에 root를 넣어서 다시 호출했을 때 __init__이 다시 실행됨
                # print("⚠ InputManager 대기 중: root가 필요합니다.")
                pass
        else:
            self._setup_rpi()
            print("[System] InputManager 초기화 완료 (RPi)")
            self.initialized = True

    def _setup_key_maps(self):
        """키 매핑 설정 (코드가 길어져서 분리함)"""
        self.key_map: Dict[InputActions, List[str]] = {
            InputActions.UP: ["Up", "w"],
            InputActions.DOWN: ["Down", "s"],
            InputActions.LEFT: ["Left", "a"],
            InputActions.RIGHT: ["Right", "d"],
            InputActions.ENTER: ["Return", "space", "z"],
            InputActions.PREV: ["bracketleft", "q"],
            InputActions.NEXT: ["bracketright", "e"],
            InputActions.ESCAPE: ["Escape"],
        }
        self._key_to_action: Dict[str, InputActions] = {}
        for action, keys in self.key_map.items():
            for key in keys:
                self._key_to_action[key] = action

    def _setup_windows(self, root: "tk.Tk"):
        root.bind("<KeyPress>", self._on_key_press)
        root.bind("<KeyRelease>", self._on_key_release)

    def _setup_rpi(self):
        try:
            from gpiozero import Button

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
            for action, btn in self.gpio_buttons.items():
                btn.when_pressed = lambda a=action: self._on_gpio_press(a)
                btn.when_released = lambda a=action: self._on_gpio_release(a)
        except ImportError:
            print("GPIO 모듈 로드 실패")
            self.gpio_buttons = {}
        except Exception as e:
            print(f"GPIO 설정 오류: {e}")

    def _on_key_press(self, event):
        sym = event.keysym
        self.state.pressed_keys.add(sym)
        action = self._key_to_action.get(sym)
        if action:
            if action not in self.state.held_actions:
                self.state.just_pressed_actions.add(action)
            self.state.held_actions.add(action)

    def _on_key_release(self, event):
        sym = event.keysym
        if sym in self.state.pressed_keys:
            self.state.pressed_keys.remove(sym)
        action = self._key_to_action.get(sym)
        if action:
            self.state.held_actions.discard(action)

    def _on_gpio_press(self, action: InputActions):
        if action not in self.state.held_actions:
            self.state.just_pressed_actions.add(action)
        self.state.held_actions.add(action)

    def _on_gpio_release(self, action: InputActions):
        self.state.held_actions.discard(action)

    def clear_just_pressed(self):
        self.state.clear_just_pressed()
