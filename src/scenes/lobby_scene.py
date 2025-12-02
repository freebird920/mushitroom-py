import time  # [추가] 시간 체크를 위해 필요
from datetime import datetime
from typing import Any, TypedDict, Unpack
import uuid

from PIL.ImageDraw import ImageDraw
from classes.mushroom_class import MushroomType
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import BaseScene
from components.cursor_component import CursorComponent
from components.mushroom_component import MushroomComponent
from components.render_image import RenderImage
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent

from managers.input_manager import InputManager
from managers.scene_manager import SceneManager
from managers.sound_manager import AudioList, SoundManager
from managers.sq_manager import SqService
from managers.ui_component_manager import UiComponentManager

from schemas.mushitroom_schema import MushitroomSchema
from schemas.user_schema import GameState
from settings.mushitroom_config import DISPLAY_WIDTH, ZOOM_IN
from settings.mushitroom_enums import FontStyle, InputActions, SceneType
from utils.name_after_mushitroom import MushroomNameGenerator


class LobbySceneArgs(TypedDict):
    user_id: str


class LobbyScene(BaseScene):
    _ui_component_manager: UiComponentManager
    _sound_manager: SoundManager
    _game_state: GameState | None
    _user_id: str | None

    _bussot_component: MushroomComponent | None  # 버섯 데이터 컴포넌트
    _bussot_ui_component: RenderUiComponent | None  # 화면에 그려지는 UI 껍데기
    _anim_last_time: float
    _anim_index: int

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

        # [추가] 애니메이션 변수 초기화
        self._bussot_component = None
        self._bussot_ui_component = None
        self._anim_last_time = time.time()
        self._anim_index = 0

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
            is_alive=True,
        )

        self.db.save_mushitroom(user_id=self._user_id, mush_data=new_mushroom)
        print("✅ DB 저장 완료!")

        self._setup_ui()

    def on_enter(self, **kwargs: Unpack[LobbySceneArgs]):
        super().on_enter(**kwargs)
        self._sound_manager.play_bgm(audio=AudioList.BGM_01)
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
        # 앞서 수정한 대로 clear_components(reset_index=False) 사용 권장
        self._ui_component_manager.clear_components(reset_index=False)

        # [수정] 버섯 컴포넌트를 self 변수에 저장 (update에서 쓰기 위해)
        self._bussot_component = MushroomComponent(
            mushroom_type=MushroomType.MAGUI,
            coordinate=RenderCoordinate(50, 50),
            size=RenderSize(50, 50),
        )

        # [수정] UI 컴포넌트도 self 변수에 저장하고, 초기 이미지는 0번으로 설정
        self._anim_index = 0
        self._bussot_ui_component = RenderUiComponent(
            is_selectable=False,
            on_activate=None,
            render_object=self._bussot_component.mushroom_images[self._anim_index],
        )

        self._ui_component_manager.add_component(self._bussot_ui_component)

        user_id_text = RenderText(
            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 10),
            color="black",
            text=f"{self._user_id}",
            size=RenderSize(0, 0),
            font_size=12,
            font_style=FontStyle.COOKIE_BOLD,
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=False,
                render_object=user_id_text,
            )
        )

        # 3. 버섯 목록 가져오기 & 그리기
        if self._user_id is not None:
            my_mushrooms = self.db.get_user_mushrooms(self._user_id)

            start_y = 60
            gap_y = 30

            if not my_mushrooms:
                self._ui_component_manager.add_component(
                    RenderUiComponent(
                        is_selectable=False,
                        render_object=RenderText(
                            font_size=12,
                            font_style=FontStyle.COOKIE_BOLD,
                            color="black",
                            text="ㅄ 없음니다.",
                            size=RenderSize(0, 0),
                            coordinate=RenderCoordinate(DISPLAY_WIDTH // 2, 100),
                        ),
                    )
                )
            else:
                for i, mush in enumerate(my_mushrooms):
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

        btn_y_pos = 200

        adopt_button = RenderImage(
            coordinate=RenderCoordinate(60, btn_y_pos),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_adopt.png",
        )

        is_adoptable: bool = False
        if self._user_id and self.db.count_alive_mushrooms(self._user_id) < 3:
            is_adoptable = True
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=is_adoptable,
                on_activate=self._on_adopt_click,
                render_object=adopt_button,
            )
        )

        dance_button = RenderImage(
            coordinate=RenderCoordinate(140, btn_y_pos),
            size=RenderSize((320 // 4) * ZOOM_IN, (100 // 4) * ZOOM_IN),
            src="./src/assets/images/btn_dance.png",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                on_activate=lambda: print("춤추기!"),
                render_object=dance_button,
            )
        )

        supply_button = RenderImage(
            coordinate=RenderCoordinate(220, btn_y_pos),
            size=RenderSize(320 // 4, 100 // 4),
            src="./src/assets/images/btn_supply.png",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                on_activate=None,
                render_object=supply_button,
            )
        )

    def handle_input(self):
        super().handle_input()
        im = InputManager()

        if im.state.is_just_pressed(InputActions.LEFT):
            self._ui_component_manager.select_prev()
        if im.state.is_just_pressed(InputActions.RIGHT):
            self._ui_component_manager.select_next()
        if im.state.is_just_pressed(InputActions.ENTER):
            self._ui_component_manager.activate_current()
        if im.state.is_just_pressed(InputActions.ESCAPE):
            scene_manager = SceneManager()
            scene_manager.switch_scene(SceneType.SELECT_USER)

    def update(self):
        super().update()

        if self._bussot_component and self._bussot_ui_component:
            current_time = time.time()

            # 0.5초가 지났는지 확인
            if current_time - self._anim_last_time >= 0.5:
                # 시간 갱신
                self._anim_last_time = current_time

                # 인덱스 증가 (0 ~ 4 순환)
                # mushroom_images 리스트 길이에 맞춰 모듈러 연산
                total_frames = len(self._bussot_component.mushroom_images)
                if total_frames > 0:
                    self._anim_index = (self._anim_index + 1) % total_frames
                    new_image = self._bussot_component.mushroom_images[self._anim_index]
                    self._bussot_ui_component.render_object = new_image

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        # update()는 보통 메인 루프에서 호출되므로, draw에서는 그리기만 함
        self._ui_component_manager.draw(draw_tool)

    def on_exit(self):
        super().on_exit()
        self._ui_component_manager.clear_components()
        self._bussot_component = None
        self._bussot_ui_component = None
        self._sound_manager.stop_bgm()
