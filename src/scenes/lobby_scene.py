from typing import Any, TypedDict, Unpack

from PIL.ImageDraw import ImageDraw
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import BaseScene
from components.render_text import RenderText
from managers.sound_manager import SoundManager
from managers.sq_manager import SqService
from managers.ui_component_manager import UiComponentManager
from schemas.user_schema import GameState, User
from settings.mushitroom_config import DISPLAY_WIDTH
from settings.mushitroom_enums import FontStyle


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

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        user_id_text = RenderText(
            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 10),
            color="black",
            text=f"{self._user_id}",
            size=RenderSize(0, 0),
            font_size=12,
            font_style=FontStyle.COOKIE_BOLD,
        )
        user_id_text.draw(draw_tool)

    def on_exit(self):
        super().on_exit()
