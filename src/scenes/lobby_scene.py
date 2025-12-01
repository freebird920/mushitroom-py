from datetime import datetime
from typing import Any, TypedDict, Unpack
import uuid

from PIL.ImageDraw import ImageDraw
from classes.mushroom_class import MushroomType
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import BaseScene
from components.cursor_component import CursorComponent
from components.render_image import RenderImage
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent

from managers.input_manager import InputManager
from managers.sound_manager import SoundManager
from managers.sq_manager import SqService
from managers.ui_component_manager import UiComponentManager

from schemas.mushitroom_schema import MushitroomSchema
from schemas.user_schema import GameState
from settings.mushitroom_config import DISPLAY_WIDTH
from settings.mushitroom_enums import FontStyle, InputActions
from utils.name_after_mushitroom import MushroomNameGenerator


class LobbySceneArgs(TypedDict):
    user_id: str


class LobbyScene(BaseScene):
    _ui_component_manager: UiComponentManager
    _sound_manager: SoundManager
    _game_state: GameState | None
    _user_id: str | None

    def __init__(self):
        super().__init__()
        self.db = SqService()
        self._user_id = None
        self._ui_component_manager = UiComponentManager(
            cursor=CursorComponent(
                coordinate=RenderCoordinate(0, 0),
                size=RenderSize(82, 30),
            )
        )
        self._sound_manager = SoundManager()

    def _on_adopt_click(self):
        print("🍄 버섯 입양 버튼 클릭됨!")

        if self._user_id is None:
            print("[Error] 유저 ID가 없어 입양할 수 없습니다.")
            return

        # 1. DB 저장 로직
        new_mush_id = str(uuid.uuid4())
        now_str = datetime.now().isoformat()

        new_mushroom = MushitroomSchema(
            user_id=self._user_id,
            id=new_mush_id,
            created=now_str,
            # [중요] 저장할 때는 문자열(.name)로 변환해서 저장
            type=MushroomType.GOMBO,
            name=MushroomNameGenerator().get_random_name(
                name=MushroomType.GOMBO.name_kr
            ),
            age=0,
            exp=0,
            level=1,
            health=100,
            talent=5,
            cute=10,
        )

        self.db.save_mushitroom(user_id=self._user_id, mush_data=new_mushroom)
        print("✅ DB 저장 완료!")

        # 2. [핵심] 화면 갱신 (UI 다시 그리기)
        # 이 함수가 없으면 DB엔 들어갔는데 화면엔 안 나옵니다.
        self._setup_ui()

    def on_enter(self, **kwargs: Unpack[LobbySceneArgs]):
        super().on_enter(**kwargs)

        self._user_id = kwargs.get("user_id")
        if not self._user_id:
            print("[Error] LobbyScene: user_id가 전달되지 않았습니다!")
            return

        # DB 로직
        game_state = self.db.get_full_game_state(self._user_id)
        if game_state is None:
            self.db.save_game_state(user_id=self._user_id, money=20, days=0)
            game_state = self.db.get_full_game_state(self._user_id)

        self._game_state = game_state
        print(f"[System] 로비 입장 완료: {self._user_id}")

        # UI 초기화
        self._setup_ui()

    def _setup_ui(self):
        """화면의 모든 요소를 지우고 다시 배치하는 함수"""
        # 1. 기존 컴포넌트 싹 비우기
        self._ui_component_manager.ui_components.clear()

        # 2. 유저 ID 텍스트
        user_id_text = RenderText(
            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 10),
            color="black",
            text=f"{self._user_id}",
            size=RenderSize(0, 0),
            font_size=12,
            font_style=FontStyle.COOKIE_BOLD,
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(is_selectable=False, render_object=user_id_text)
        )

        # 3. 버섯 목록 가져오기 & 그리기

        if self._user_id is not None:
            my_mushrooms = self.db.get_user_mushrooms(self._user_id)

            start_y = 60
            gap_y = 30  # 간격 조정

            if not my_mushrooms:
                # 버섯 없을 때
                self._ui_component_manager.add_component(
                    RenderUiComponent(
                        is_selectable=False,
                        render_object=RenderText(
                            font_size=12,
                            font_style=FontStyle.COOKIE_BOLD,
                            color="black",
                            text="보유한 버섯이 없습니다.",
                            size=RenderSize(0, 0),
                            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 100),
                        ),
                    )
                )
            else:
                # 버섯 있을 때 리스트 출력
                for i, mush in enumerate(my_mushrooms):
                    # Enum 객체 처리 (Enum이면 .name_kr, 문자열이면 그냥 출력)

                    display_text = f"{i+1}. {mush.name} (Lv.{mush.level})"

                    self._ui_component_manager.add_component(
                        RenderUiComponent(
                            is_selectable=False,
                            render_object=RenderText(
                                font_size=10,
                                font_style=FontStyle.COOKIE_BOLD,
                                color="black",
                                text=display_text,
                                size=RenderSize(0, 0),
                                coordinate=RenderCoordinate(
                                    x=DISPLAY_WIDTH // 2,
                                    y=start_y + (i * gap_y),
                                ),
                            ),
                        )
                    )

        # 4. 버튼들 다시 배치 (좌표가 겹치지 않게 Y값 조정 필요할 수 있음)
        btn_y_pos = 200  # 버튼 위치

        adopt_button = RenderImage(
            coordinate=RenderCoordinate(60, btn_y_pos),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_adopt.png",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                on_activate=self._on_adopt_click,  # 재연결
                render_object=adopt_button,
            )
        )

        dance_button = RenderImage(
            coordinate=RenderCoordinate(140, btn_y_pos),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_dance.png",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                on_activate=lambda: print("춤추기!"),
                render_object=dance_button,
            )
        )

    def handle_input(self, input_state=None):  # 인자 없어도 됨 (싱글톤 사용)
        super().handle_input()
        im = InputManager()

        if im.state.is_just_pressed(InputActions.LEFT):
            self._ui_component_manager.select_prev()
        if im.state.is_just_pressed(InputActions.RIGHT):
            self._ui_component_manager.select_next()
        if im.state.is_just_pressed(InputActions.ENTER):
            self._ui_component_manager.activate_current()

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self._ui_component_manager.draw(draw_tool)

    def on_exit(self):
        super().on_exit()
