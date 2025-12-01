from typing import TYPE_CHECKING, Any, Unpack


from src.managers.scene_manager import SceneManager

if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from PIL.ImageDraw import ImageDraw


class BaseScene:
    manager: "SceneManager"

    def __init__(
        self,
    ):
        self.manager = SceneManager()

    def handle_input(self, input_state: "InputState"):
        """키 입력 처리"""
        pass

    def update(self):
        """게임 로직 업데이트 (이동, 충돌 등)"""
        pass

    def draw(self, draw_tool: "ImageDraw"):
        """화면 그리기"""
        pass

    def on_enter(self, **kwargs: Any):
        """씬에 진입할 때 실행 (초기화)"""
        pass

    def on_exit(self):
        """씬을 나갈 때 실행 (정리)"""
        pass
