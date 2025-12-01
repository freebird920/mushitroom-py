from typing import Any, TypedDict, Unpack

from PIL.ImageDraw import ImageDraw
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import BaseScene
from components.render_button import RenderButton
from components.render_image import RenderImage
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent
from managers.input_manager import InputState
from managers.sound_manager import SoundManager
from managers.sq_manager import SqService
from managers.ui_component_manager import UiComponentManager
from schemas.user_schema import GameState, User
from settings.mushitroom_config import DISPLAY_WIDTH
from settings.mushitroom_enums import FontStyle, InputActions


class LobbySceneArgs(TypedDict):
    user_id: str


class LobbyScene(BaseScene):
    _ui_component_manager: UiComponentManager
    _sound_manager: SoundManager
    _game_state: GameState | None
    _user_id: str | None
    _ui_manager: UiComponentManager

    def __init__(self):
        super().__init__()
        self.db = SqService()
        self._user_id = None
        self._ui_component_manager = UiComponentManager()
        self._sound_manager = SoundManager()

    def on_enter(self, **kwargs: Unpack[LobbySceneArgs]):
        super().on_enter(**kwargs)

        # 1. 안전하게 user_id 가져오기
        self._user_id = kwargs.get("user_id")

        if not self._user_id:
            print("[Error] LobbyScene: user_id가 전달되지 않았습니다!")
            return

        # 2. DB 로직 수행
        game_state = self.db.get_full_game_state(self._user_id)

        if game_state is None:
            self.db.save_game_state(
                user_id=self._user_id,
                money=20,
                days=0,
            )
            # 저장 후 다시 불러오기
            game_state = self.db.get_full_game_state(self._user_id)

        self._game_state = game_state
        print(f"[System] 로비 입장 완료: {self._user_id}")

        user_id_text = RenderText(
            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 10),
            color="black",
            text=f"{self._user_id}",
            size=RenderSize(0, 0),
            font_size=12,
            font_style=FontStyle.COOKIE_BOLD,
        )
        user_id_text_component = RenderUiComponent(
            is_selectable=False,
            on_activate=None,
            render_object=user_id_text,
        )
        self._ui_component_manager.add_component(user_id_text_component)

        dance_button = RenderImage(
            coordinate=RenderCoordinate(60, 200),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_adopt.png",
        )
        dance_button_component = RenderUiComponent(
            is_selectable=True,
            on_activate=None,
            render_object=dance_button,
        )
        self._ui_component_manager.add_component(dance_button_component)
        dance_button = RenderImage(
            coordinate=RenderCoordinate(140, 200),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_dance.png",
        )
        dance_button_component = RenderUiComponent(
            is_selectable=True,
            on_activate=None,
            render_object=dance_button,
        )
        self._ui_component_manager.add_component(dance_button_component)

    def handle_input(self, input_state: InputState):
        if InputActions.DOWN in input_state.just_pressed_actions:
            print("눌림")
        return super().handle_input(input_state)

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self._ui_component_manager.draw(draw_tool)

        # user_id_text.draw(draw_tool)

    def on_exit(self):
        super().on_exit()
