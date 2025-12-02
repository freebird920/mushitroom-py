from typing import TYPE_CHECKING

# import classes
from managers.input_manager import InputManager
from managers.sq_manager import SqService
from schemas.user_schema import User
from components.cursor_component import CursorComponent
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import BaseScene

# import settings
from settings import mushitroom_config
from settings.mushitroom_enums import InputActions

# import utils
from utils.name_generator import NameGenerator

# import components
from components.render_ui_component import RenderUiComponent
from components.render_button import RenderButton

# import managers
from managers.scene_manager import SceneType
from managers.ui_component_manager import UiComponentManager
from managers.sound_manager import AudioList, SoundManager


if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw

# [설정] 레이아웃 미세 조정을 위한 오프셋 (직접 수정 가능)
# 만약 화면 오른쪽으로 치우쳐 보인다면 이 값을 -50, -100 등으로 줄여보세요.
# 만약 더블 줌(4배) 현상이 의심된다면 -55 정도로 설정하면 해결될 수 있습니다.
LAYOUT_OFFSET_X = 0


class SelectUserScene(BaseScene):
    _ui_component_manager: UiComponentManager
    _sound_fx_manager: SoundManager
    _input_manager: InputManager

    def __init__(self):
        super().__init__()
        self.db = SqService()
        self._sound_fx_manager = SoundManager()
        self.users = []
        self._input_manager = InputManager()

        # --- 레이아웃 설정 ---
        self.scroll_y = 0

        # 버튼 설정 (논리적 크기)
        self.btn_width = 100
        self.btn_height = 30
        self.btn_gap = 10  # 버튼 사이 간격
        self.list_start_y = 60  # 리스트 시작 Y 위치

        # 커서 설정
        cursor_width = self.btn_width + 4
        cursor_height = self.btn_height + 4

        # 초기 커서 컴포넌트 설정
        self._ui_component_manager = UiComponentManager(
            cursor=CursorComponent(
                coordinate=RenderCoordinate(0, 0),
                size=RenderSize(cursor_width, cursor_height),
            )
        )

    def on_enter(self, **args):
        print("=== 사용자 선택 화면 진입 ===")
        self._sound_fx_manager.play_bgm(AudioList.BGM_02)
        self.scroll_y = 0
        self._ui_component_manager.clear_components()

        # DB에서 유저 조회
        self.users = self.db.get_all_users()

        # [중앙 정렬 로직]
        try:
            # mushitroom_config.CENTER_X 사용 (없으면 기본값 160)
            center_x = getattr(mushitroom_config, "CENTER_X", 160)
        except AttributeError:
            center_x = 160

        # 기본 계산: 중앙 - (버튼너비 / 2)
        base_align_x = center_x - (self.btn_width // 2)

        # [수정] 오프셋 적용 (강제 보정)
        # 렌더링 단계의 좌표 왜곡을 상쇄하기 위해 오프셋을 더합니다.
        final_align_x = base_align_x + LAYOUT_OFFSET_X

        # [디버그] 최종 적용 좌표 확인
        print(
            f"[DEBUG] Center: {center_x}, BaseAlign: {base_align_x}, FinalAlign: {final_align_x} (Offset: {LAYOUT_OFFSET_X})"
        )

        # 1. 상단 [NEW USER] 버튼 생성
        new_user_y = 20  # 상단 여백
        render_button = RenderButton(
            coordinate=RenderCoordinate(x=final_align_x, y=new_user_y),
            size=RenderSize(width=self.btn_width, height=self.btn_height),
            font_size=10,
            text="[ NEW USER ]",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                render_object=render_button,
                on_activate=lambda: self.create_new_user(),
            )
        )

        # 2. 유저 목록 버튼 생성
        current_y = self.list_start_y

        for i, user in enumerate(self.users):
            user_btn = RenderButton(
                coordinate=RenderCoordinate(x=final_align_x, y=current_y),
                size=RenderSize(width=self.btn_width, height=self.btn_height),
                text=f"{user.username}",
            )

            ui_component = RenderUiComponent(
                render_object=user_btn,
                is_selectable=True,
                on_activate=lambda u=user: self.select_user(u),
            )

            self._ui_component_manager.add_component(ui_component)

            # 다음 버튼 Y 좌표
            current_y += self.btn_height + self.btn_gap

    def select_user(self, user: User):
        print(f"유저 선택됨: {user.username}")
        self.manager.switch_scene(
            scene_type=SceneType.LOBBY_SCENE,
            user_id=user.id,
        )

    def create_new_user(self):
        print("새 유저 생성")
        random_name = NameGenerator().get_random_name()
        self.db.create_user(f"{random_name}")
        self.on_enter()

    def handle_input(self):
        if self._input_manager.state.is_just_pressed(InputActions.UP):
            self._ui_component_manager.select_prev()
        elif self._input_manager.state.is_just_pressed(InputActions.DOWN):
            self._ui_component_manager.select_next()
        elif self._input_manager.state.is_just_pressed(InputActions.ENTER):
            self._ui_component_manager.activate_current()

    def update(self):
        pass

    def draw(self, draw_tool: "ImageDraw"):
        self._ui_component_manager.draw(draw_tool)

    def on_exit(self):
        print("=== 사용자 선택 화면 퇴장 ===")
        self._ui_component_manager.selected_index = -1
        self.scroll_y = 0
        self._sound_fx_manager.stop_bgm()
