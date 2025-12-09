from typing import TYPE_CHECKING, Any

from managers.audio_manager import AudioManager
from managers.input_manager.input_manager import InputManager
from managers.sq_manager import SqManager
from managers.timer_manager import TimerManager
from managers.ui_component_manager import UiComponentManager


if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw
    from managers.scene_manager import SceneManager


class BaseScene:
    _timer_manager: TimerManager
    _scene_manager: "SceneManager"
    _audio_manager: AudioManager
    _input_manager: InputManager
    _ui_manager: UiComponentManager
    db: SqManager

    def __init__(
        self,
    ):
        from managers.scene_manager import SceneManager

        self._timer_manager = TimerManager()
        self._scene_manager = SceneManager()
        self._audio_manager = AudioManager()
        self._input_manager = InputManager()
        self._ui_manager = UiComponentManager()
        self.db = SqManager()

    def handle_input(
        self,
    ):
        """키 입력 처리"""
        pass

    def update(self):
        self._timer_manager.update()
        """게임 로직 업데이트 (이동, 충돌 등)"""
        pass

    def draw(self, draw_tool: "ImageDraw"):
        """화면 그리기"""
        pass

    def on_enter(self, **kwargs: Any):
        self._ui_manager.clear_components()
        """씬에 진입할 때 실행 (초기화)"""
        pass

    def on_exit(self):
        """씬을 나갈 때 실행 (정리)"""
        self._ui_manager.clear_components()
        self._timer_manager.clear_all_intervals()
        pass
