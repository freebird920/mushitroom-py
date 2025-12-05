from typing import TypedDict, Unpack

from PIL.ImageDraw import ImageDraw
from classes.mushroom_class import MushroomType
from classes.scene_base import BaseScene
from managers.ui_component_manager import UiComponentManager
from scenes.mushroom_select_scene import logic, ui_builder
from schemas.mushitroom_schema import MushitroomSchema
from schemas.user_schema import GameState
from settings.mushitroom_enums import InputActions, SceneType
from utils.new_mushroom import new_mushroom


class SelectMushroomSceneArgs(TypedDict):
    user_id: str


class SelectMushroomScene(BaseScene):
    _user_id: str
    _game_state: GameState | None
    _mushroom_ui_manager: UiComponentManager

    def __init__(self):
        self._user_id = ""
        self._mushroom_ui_manager = UiComponentManager()
        super().__init__()

    def adopt_mushroom(self):
        new_mushroom(
            user_id=self._user_id,
            mushroom_type=MushroomType.get_random(),
        )

    def on_enter(self, **kwargs: Unpack[SelectMushroomSceneArgs]):
        super().on_enter(**kwargs)
        self._user_id = kwargs.get("user_id")
        if self._user_id is None or self._user_id == "":
            print("USER_NAME NONE!")
            self._scene_manager.switch_scene(SceneType.TITLE_SCENE)
        logic.initialize_user(self)
        ui_builder.build_mushroom_select_scene_ui(self)
        ui_builder.build_mushrooms(self)

    def handle_input(self):
        super().handle_input()
        if self._input_manager.state.is_just_pressed(InputActions.ESCAPE):
            self._scene_manager.switch_scene(SceneType.TITLE_SCENE)
        if self._input_manager.state.is_just_pressed(InputActions.LEFT):
            self._ui_manager.select_prev()
            self._mushroom_ui_manager.select_prev()
        if self._input_manager.state.is_just_pressed(InputActions.RIGHT):
            self._ui_manager.select_next()
            self._mushroom_ui_manager.select_next()
        if self._input_manager.state.is_just_pressed(InputActions.UP):
            self._ui_manager.disable(True)
            self._mushroom_ui_manager.disable(False)
        if self._input_manager.state.is_just_pressed(InputActions.DOWN):
            self._ui_manager.disable(False)
            self._mushroom_ui_manager.disable(True)
        if self._input_manager.state.is_just_pressed(InputActions.ENTER):
            self._ui_manager.activate_current()

    def on_exit(self):
        self._mushroom_ui_manager.clear_components()

        return super().on_exit()

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self._mushroom_ui_manager.draw(draw_tool)
        self._ui_manager.draw(draw_tool)

    def update(self):
        return super().update()
