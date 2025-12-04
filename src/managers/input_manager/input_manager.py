from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Set, Dict, List, Optional
from settings.mushitroom_enums import InputActions
from settings import mushitroom_config

if TYPE_CHECKING:
    import tkinter as tk


# -------------------------------------------------------------------------
# [Data Class] 입력 상태 저장소
# -------------------------------------------------------------------------
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


# -------------------------------------------------------------------------
# [Strategy Interface] 입력 처리 전략 (추상 클래스)
# -------------------------------------------------------------------------
class InputStrategy(ABC):
    def __init__(self, state: InputState):
        self.state = state

    @abstractmethod
    def setup(self, **kwargs):
        """플랫폼별 초기화 로직 (예: bind, gpio setup)"""
        pass

    def _update_action_state(self, action: InputActions, is_pressed: bool):
        """입력 상태 갱신 공통 로직"""
        if is_pressed:
            if action not in self.state.held_actions:
                self.state.just_pressed_actions.add(action)
            self.state.held_actions.add(action)
        else:
            self.state.held_actions.discard(action)


# -------------------------------------------------------------------------
# [Concrete Strategy 1] Windows (Tkinter) 구현
# -------------------------------------------------------------------------
class WindowsInputStrategy(InputStrategy):
    def setup(self, **kwargs):
        root: "tk.Tk | None" = kwargs.get("root")
        if not root:
            print("⚠ WindowsInputStrategy: root 객체가 필요합니다.")
            return

        self._setup_key_maps()
        root.bind("<KeyPress>", self._on_key_press)
        root.bind("<KeyRelease>", self._on_key_release)
        print("[System] Input Strategy: Windows (Keyboard) Connected")

    def _setup_key_maps(self):
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

    def _on_key_press(self, event):
        sym = event.keysym
        self.state.pressed_keys.add(sym)
        action = self._key_to_action.get(sym)
        if action:
            self._update_action_state(action, is_pressed=True)

    def _on_key_release(self, event):
        sym = event.keysym
        if sym in self.state.pressed_keys:
            self.state.pressed_keys.remove(sym)
        action = self._key_to_action.get(sym)
        if action:
            self._update_action_state(action, is_pressed=False)


# -------------------------------------------------------------------------
# [Concrete Strategy 2] Raspberry Pi (GPIO) 구현
# -------------------------------------------------------------------------
class RpiInputStrategy(InputStrategy):
    def setup(self, **kwargs):
        try:
            from gpiozero import Button

            # GPIO 버튼 설정
            self.gpio_buttons = {
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

            # 이벤트 바인딩
            for action, btn in self.gpio_buttons.items():
                btn.when_pressed = lambda a=action: self._update_action_state(a, True)
                btn.when_released = lambda a=action: self._update_action_state(a, False)

            print("[System] Input Strategy: Raspberry Pi (GPIO) Connected")

        except ImportError:
            print("❌ GPIO 모듈 로드 실패 (gpiozero가 설치되어 있나요?)")
        except Exception as e:
            print(f"❌ GPIO 설정 오류: {e}")


# -------------------------------------------------------------------------
# [Context] Input Manager (Singleton)
# -------------------------------------------------------------------------
class InputManager:
    _instance: Optional["InputManager"] = None
    state: InputState
    strategy: InputStrategy
    initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_windows: bool = True):
        """
        초기화 시에는 플랫폼 결정만 합니다.
        실제 바인딩(setup)은 initialize() 메서드에서 수행합니다.
        """
        if hasattr(self, "initialized") and self.initialized:
            return

        self.state = InputState()

        # 전략 선택 (Factory Logic)
        if is_windows:
            self.strategy = WindowsInputStrategy(self.state)
        else:
            self.strategy = RpiInputStrategy(self.state)

    def initialize(self, root: "tk.Tk | None" = None):
        """
        외부에서 적절한 시점(예: 윈도우 생성 직후)에 호출해야 합니다.
        """
        if self.initialized:
            return

        self.strategy.setup(root=root)
        self.initialized = True

    def clear_just_pressed(self):
        """매 프레임 호출"""
        self.state.clear_just_pressed()
