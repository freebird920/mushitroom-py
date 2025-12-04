from typing import TypedDict, Unpack

from PIL.ImageDraw import ImageDraw
from classes.scene_base import BaseScene
from scenes.mushroom_select_scene import logic, ui_builder
from schemas.user_schema import GameState
from settings.mushitroom_enums import InputActions, SceneType


class SelectMushroomSceneArgs(TypedDict):
    user_id: str


class SelectMushroomScene(BaseScene):
    _user_id: str
    _game_state: GameState | None

    def __init__(self):
        self._user_id = ""
        super().__init__()

    def on_enter(self, **kwargs: Unpack[SelectMushroomSceneArgs]):
        super().on_enter(**kwargs)
        self._user_id = kwargs.get("user_id")
        logic.initialize_user(self)
        ui_builder.build_mushroom_select_scene_ui(self)

    def handle_input(self):
        super().handle_input()
        if self._input_manager.state.is_just_pressed(InputActions.ESCAPE):
            self._scene_manager.switch_scene(SceneType.TITLE_SCENE)
        if self._input_manager.state.is_just_pressed(InputActions.UP):
            self._ui_manager.select_prev()
        if self._input_manager.state.is_just_pressed(InputActions.DOWN):
            self._ui_manager.select_next()
        if self._input_manager.state.is_just_pressed(InputActions.ENTER):
            self._ui_manager.activate_current()

    def on_exit(self):

        return super().on_exit()

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self._ui_manager.draw(draw_tool)
