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
    from managers.input_manager import InputState
    from PIL.ImageDraw import ImageDraw


class SelectUserScene(BaseScene):
    _ui_component_manager: UiComponentManager
    _sound_fx_manager: SoundManager
    _input_manager: InputManager

    def __init__(
        self,
    ):
        super().__init__()
        self.db = SqService()
        self._sound_fx_manager = SoundManager()
        self.users = []
        self._input_manager = InputManager()
        # --- 스크롤 설정을 위한 변수들 ---
        self.scroll_y = 0  # 현재 스크롤된 양
        self.list_stt_y = 60  # 리스트가 시작되는 Y 위치
        self.item_height = 50  # 각 버튼의 높이 + 간격
        # 화면의 높이 (manager에 screen_height가 있다고 가정하거나 상수로 지정)
        # 예: 전체 600px 중 하단 여백 등을 뺀 리스트가 보일 수 있는 최대 높이 설정
        self.visible_height = mushitroom_config.DISPLAY_HEIGHT
        self._ui_component_manager = UiComponentManager(
            cursor=CursorComponent(
                coordinate=RenderCoordinate(0, 0),
                size=RenderSize(102, 36),
            )
        )

    def on_enter(self, **args):
        print("=== 사용자 선택 화면 진입 ===")
        self._sound_fx_manager.play_bgm(AudioList.BGM_02)
        self.scroll_y = 0  # 스크롤 초기화
        self._ui_component_manager.clear_components()
        # DB에서 유저 조회
        self.users = self.db.get_all_users()
        render_button = RenderButton(
            coordinate=RenderCoordinate(
                x=mushitroom_config.DISPLAY_WIDTH // 2,
                y=15,
            ),
            size=RenderSize(
                width=100,
                height=30,
            ),
            font_size=10,
            text="user_select",
        )
        self._ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=True,
                render_object=render_button,
                on_activate=lambda: self.create_new_user(),
            )
        )
        current_height = 60
        # 2. 유저 목록 버튼 생성
        # Y좌표는 나중에 update()에서 계산하므로 여기선 초기 순서만 중요함
        for i, user in enumerate(self.users):
            button_shit = RenderButton(
                coordinate=RenderCoordinate(
                    x=mushitroom_config.DISPLAY_WIDTH // 2,
                    y=current_height,
                ),
                size=RenderSize(
                    width=100,
                    height=30,
                ),
                text=f"{user.username}",
            )
            render_button_shit = RenderUiComponent(
                render_object=button_shit,
                is_selectable=True,
                on_activate=lambda u=user: self.select_user(u),
            )

            self._ui_component_manager.add_component(render_button_shit)
            current_height = current_height + 50
        # 3. 새 유저 생성 버튼

    def select_user(self, user: User):
        print(f"유저 선택됨: {user.username}")
        self.manager.switch_scene(
            scene_type=SceneType.LOBBY_SCENE,
            user_id=user.id,
        )
        pass

    def create_new_user(self):
        print("새 유저 생성")
        self.db.create_user(f"{NameGenerator().get_random_name()}")
        self.on_enter()

    def handle_input(self):

        if self._input_manager.state.is_just_pressed(InputActions.UP):
            self._ui_component_manager.select_prev()
        if self._input_manager.state.is_just_pressed(InputActions.DOWN):
            self._ui_component_manager.select_next()
        if self._input_manager.state.is_just_pressed(InputActions.ENTER):
            self._ui_component_manager.activate_current()
        # if InputActions.UP in actions or InputActions.PREV in actions:

        # if InputActions.DOWN in actions or InputActions.NEXT in actions:
        #     self.ui_component_manager.select_next()

        # if InputActions.ENTER in actions:
        #     self.ui_component_manager.activate_current()

    def update(self):
        pass

    def draw(self, draw_tool: "ImageDraw"):
        self._ui_component_manager.draw(draw_tool)
        pass

    def on_exit(self):
        print("=== 사용자 선택 화면 퇴장 ===")
        self._ui_component_manager.selected_index = -1
        self.scroll_y = 0
        self._sound_fx_manager.stop_bgm()
