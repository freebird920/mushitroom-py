from src.classes.scene_base import BaseScene


class SceneManager:

    def __init__(self, db_instance):
        self.current_scene = None
        self.db = db_instance

    def switch_scene(self, new_scene: BaseScene):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = new_scene
        self.current_scene.on_enter()

    def handle_input(self, input_state):
        if self.current_scene:
            self.current_scene.handle_input(input_state)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, draw_tool):
        if self.current_scene:
            self.current_scene.draw(draw_tool)
