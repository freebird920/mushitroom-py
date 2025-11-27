from typing import TYPE_CHECKING
from src.services.sq_service import SqService
from classes.input_manager import InputState
from src.classes.scene_base import BaseScene

if TYPE_CHECKING:
    from PIL import ImageDraw


class SceneService:
    current_scene: BaseScene | None = None

    def __init__(self, db_instance: SqService):
        self.current_scene = None
        self.db = db_instance  # DB를 매니저가 들고 있게 함

    def switch_scene(self, new_scene: BaseScene):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = new_scene
        self.current_scene.on_enter()

    def handle_input(self, input_state: InputState):
        if self.current_scene:
            self.current_scene.handle_input(input_state)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, draw_tool: ImageDraw.ImageDraw):
        if self.current_scene:
            self.current_scene.draw(draw_tool)
