import time
from typing import TypedDict, Unpack, TYPE_CHECKING

from classes.scene_base import BaseScene
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.cursor_component import CursorComponent
from managers.input_manager.input_manager import InputManager

# [수정 1] SceneManager 상단 import 제거 (순환 참조 방지)
from managers.audio_manager import AudioList, AudioManager
from managers.sq_manager import SqManager
from managers.ui_component_manager import UiComponentManager
from settings.mushitroom_enums import InputActions, SceneType

# 분리한 모듈 임포트
from . import logic
from . import ui_builder

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw
    from components.mushroom_component import MushroomComponent
    from components.render_ui_component import RenderUiComponent
    from schemas.user_schema import GameState


class LobbySceneArgs(TypedDict):
    user_id: str


class LobbyScene(BaseScene):
    ui_component_manager: UiComponentManager
    db: SqManager

    user_id: str | None
    game_state: "GameState | None"

    # UI 관련 상태
    bussot_component: "MushroomComponent | None"
    bussot_ui_component: "RenderUiComponent | None"
    anim_last_time: float
    anim_index: int

    def __init__(self):
        super().__init__()
        self.db = SqManager()
        self.user_id = None

        # UI 매니저 초기화
        self.ui_component_manager = UiComponentManager(
            cursor=CursorComponent(
                coordinate=RenderCoordinate(0, 0),
                size=RenderSize(82, 30),
            )
        )

        self.bussot_component = None
        self.bussot_ui_component = None
        self.anim_last_time = time.time()
        self.anim_index = 0

    def on_enter(self, **kwargs: Unpack[LobbySceneArgs]):
        super().on_enter(**kwargs)
        self._audio_manager.play_bgm(audio=AudioList.BGM_01)

        self.user_id = kwargs.get("user_id")

        # [Logic] 데이터 초기화 로직 위임
        logic.check_and_initialize_user(self)

        # [View] UI 빌드 위임
        ui_builder.build_lobby_ui(self)

    def handle_adopt(self):
        """UI 버튼에서 호출할 입양 메서드"""
        logic.adopt_mushroom(self)

    def handle_feed(self):
        logic.feed_mushroom(self)

    def update(self):
        super().update()
        if self.bussot_component and self.bussot_ui_component:
            self.bussot_ui_component.render_object = self.bussot_component.rotate(True)

    def handle_input(self):
        super().handle_input()
        im = InputManager()

        if im.state.is_just_pressed(InputActions.LEFT):
            self.ui_component_manager.select_prev()
        if im.state.is_just_pressed(InputActions.RIGHT):
            self.ui_component_manager.select_next()
        if im.state.is_just_pressed(InputActions.ENTER):
            self.ui_component_manager.activate_current()
        if im.state.is_just_pressed(InputActions.ESCAPE):
            # [수정 3] 여기서 import (지연 로딩)
            from managers.scene_manager import SceneManager

            SceneManager().switch_scene(SceneType.SELECT_USER)

    def draw(self, draw_tool: "ImageDraw"):
        super().draw(draw_tool)
        self.ui_component_manager.draw(draw_tool)

    def on_exit(self):
        super().on_exit()
        self.ui_component_manager.clear_components()
        self.bussot_component = None
        self.bussot_ui_component = None
        self._audio_manager.stop_bgm()
