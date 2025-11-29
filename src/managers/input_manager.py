from typing import TYPE_CHECKING, Set, Dict, List, Optional
from src.settings import mushitroom_config

if TYPE_CHECKING:
    import tkinter as tk

class InputState:
    """현재 프레임의 입력 상태를 저장하는 데이터 클래스"""
    def __init__(self):
        # 지속적인 상태 (누르고 있는 동안 True)
        self.up: bool = False
        self.down: bool = False
        self.left: bool = False
        self.right: bool = False
        self.enter: bool = False
        self.prev: bool = False
        self.next: bool = False

        # 물리적 키 상태
        self.pressed_keys: Set[str] = set()
        self.just_pressed_keys: Set[str] = set()
        
        # [추가] 논리적 액션 상태 (이번 프레임에 막 눌린 행동들)
        # 예: 'q'를 누르면 여기에 'prev'가 들어감
        self.just_pressed_actions: Set[str] = set()


class InputManager:
    def __init__(self, is_windows: bool, root: "tk.Tk | None" = None):
        self.state = InputState()
        self.is_windows = is_windows

        # 키 매핑: 논리적 동작 -> 물리적 키 리스트
        self.key_map: Dict[str, List[str]] = {
            "up": ["Up", "w"],
            "down": ["Down", "s"],
            "left": ["Left", "a"],
            "right": ["Right", "d"],
            "enter": ["Return", "space"], # space도 엔터로 처리하면 편함
            "prev": ["bracketleft", "q", "Left"], # 왼쪽 화살표도 prev로
            "next": ["bracketright", "e", "Right"], # 오른쪽 화살표도 next로
        }

        # [최적화] 역방향 매핑 생성 (물리적 키 -> 논리적 동작)
        # 예: {'q': 'prev', 'Up': 'up', ...}
        self._key_to_action: Dict[str, str] = {}
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
        # ... (기존 GPIO 코드 유지) ...
        pass

    def _on_key_press(self, event):
        sym = event.keysym
        
        # 1. 물리적 키 기록
        if sym not in self.state.pressed_keys:
            self.state.just_pressed_keys.add(sym)
            
            # 2. [핵심] 논리적 액션 매핑 및 기록
            # 키가 눌린 '순간'에만 액션을 트리거함
            action = self._key_to_action.get(sym)
            if action:
                self.state.just_pressed_actions.add(action)
                self._update_logical_bool(action, True)

        self.state.pressed_keys.add(sym)

    def _on_key_release(self, event):
        sym = event.keysym
        if sym in self.state.pressed_keys:
            self.state.pressed_keys.remove(sym)
            
        action = self._key_to_action.get(sym)
        if action:
            self._update_logical_bool(action, False)

    def _update_logical_bool(self, action: str, is_pressed: bool):
        """논리적 상태(boolean) 업데이트 (setattr 활용)"""
        if hasattr(self.state, action):
            setattr(self.state, action, is_pressed)

    def clear_just_pressed(self):
        """프레임 종료 후 트리거 초기화"""
        self.state.just_pressed_keys.clear()
        self.state.just_pressed_actions.clear() # 액션도 초기화