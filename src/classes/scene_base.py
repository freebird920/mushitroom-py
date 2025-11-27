from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from PIL import ImageDraw
    from managers.scene_manager import SceneManager
    from src.classes.input_manager import InputState


class BaseScene:
    def __init__(self, manager: "SceneManager"):
        self.manager = manager  # 씬 전환을 위해 매니저를 알고 있어야 함

    def handle_input(self, input_state: "InputState"):
        """키 입력 처리"""
        pass

    def update(self):
        """게임 로직 업데이트 (이동, 충돌 등)"""
        pass

    def draw(self, draw_tool: "ImageDraw.ImageDraw"):
        """화면 그리기"""
        pass

    def on_enter(self):
        """씬에 진입할 때 실행 (초기화)"""
        pass

    def on_exit(self):
        """씬을 나갈 때 실행 (정리)"""
        pass
