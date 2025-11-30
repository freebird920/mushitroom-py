from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.render_button import RenderButton
from src.settings import mushitroom_config
from src.components.mushitroom_button import MushitroomButton
from src.classes.mushitroom_interface_object import (
    MushitroomInterfaceGroup,
    MushitroomInterfaceObject,
)


from src.settings.mushitroom_enums import FontStyle, InputActions
from src.utils.name_generator import NameGenerator
from src.classes.scene_base import BaseScene
from src.managers.scene_manager import SceneType

# from src.schemas.user_schema import User
from src.components.ui_cursor import UiCursor

if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from src.managers.scene_manager import SceneManager


class SelectUserScene(BaseScene):
    def __init__(self, manager: "SceneManager", db):
        super().__init__(manager, db)
        self.db = db
        self.ui_manager = MushitroomInterfaceGroup()
        self.users = []
        self.cursor = UiCursor(padding=6, color="#FF0000", line_width=3)
        # --- 스크롤 설정을 위한 변수들 ---
        self.scroll_y = 0  # 현재 스크롤된 양
        self.list_start_y = 60  # 리스트가 시작되는 Y 위치
        self.item_height = 50  # 각 버튼의 높이 + 간격
        # 화면의 높이 (manager에 screen_height가 있다고 가정하거나 상수로 지정)
        # 예: 전체 600px 중 하단 여백 등을 뺀 리스트가 보일 수 있는 최대 높이 설정
        self.visible_height = mushitroom_config.DISPLAY_HEIGHT

    def on_enter(self):
        print("=== 사용자 선택 화면 진입 ===")
        self.ui_manager.elements.clear()
        self.scroll_y = 0  # 스크롤 초기화

        # DB에서 유저 조회
        self.users = self.db.get_all_users()

        # 1. 고정 타이틀 (스크롤 영향을 받지 않음)
        title = MushitroomButton(
            index=None,
            x=100,
            y=25,
            width=200,
            height=50,
            color="black",
            text="SELECT USER",
            is_focusable=False,
            font_weight=FontStyle.COOKIE_BOLD,
            text_color="white",
        )
        self.ui_manager.add_element(title)

        # 2. 유저 목록 버튼 생성
        # Y좌표는 나중에 update()에서 계산하므로 여기선 초기 순서만 중요함
        for i, user in enumerate(self.users):
            btn = MushitroomButton(
                index=i,
                x=100,
                y=self.list_start_y + (i * self.item_height),  # 초기 위치
                width=200,
                height=50,
                color="#000000",
                text=f"{user.username}",
                font_weight=FontStyle.COOKIE_BOLD,
                on_action=lambda u=user: self.select_user(u),
            )
            self.ui_manager.add_element(btn)

        # 3. 새 유저 생성 버튼
        new_user_index = len(self.users)
        btn_create = MushitroomInterfaceObject(
            index=new_user_index,
            x=80,
            y=self.list_start_y + (new_user_index * self.item_height),  # 초기 위치
            width=200,
            height=40,
            color="#AAAAFF",
            text="+ NEW USER",
            font_weight=FontStyle.HEAVY,
            on_action=self.create_new_user,
        )
        self.ui_manager.add_element(btn_create)

    def select_user(self, user):
        print(f"유저 선택됨: {user.username}")
        self.manager.switch_scene(
            scene_type=SceneType.USER_TEST,
            user=user,
        )
        pass

    def create_new_user(self):
        print("새 유저 생성")
        self.db.create_user(f"{NameGenerator().get_random_name()}")
        self.on_enter()

    def handle_input(self, input_state: "InputState"):
        actions = input_state.just_pressed_actions

        if InputActions.UP in actions or InputActions.PREV in actions:
            self.ui_manager.select_prev()

        if InputActions.DOWN in actions or InputActions.NEXT in actions:
            self.ui_manager.select_next()

        if InputActions.ENTER in actions:
            self.ui_manager.execute_current()

    def update(self):
        # === 스크롤 로직 (기존 코드 유지) ===
        current_idx = self.ui_manager.current_index
        if current_idx < 0:
            return

        target_y = self.list_start_y + (current_idx * self.item_height)

        if target_y < self.list_start_y + self.scroll_y:
            self.scroll_y = target_y - self.list_start_y
        elif (
            target_y
            > self.list_start_y + self.scroll_y + self.visible_height - self.item_height
        ):
            self.scroll_y = target_y - (
                self.list_start_y + self.visible_height - self.item_height
            )

        # 4. 모든 UI 요소 위치 업데이트 (기존 코드 유지)
        current_obj = None  # [변경] 현재 선택된 객체를 찾기 위한 변수

        for elem in self.ui_manager.elements:
            if elem.index == None:
                continue

            original_y = self.list_start_y + (elem.index * self.item_height)
            elem.y = original_y - self.scroll_y

            if elem.index == current_idx:
                current_obj = elem

        if current_obj:
            self.cursor.set_target(current_obj)
            self.cursor.update()

    def draw(self, draw_tool):
        render_button = RenderButton(
            coordinate=RenderCoordinate(x=40, y=40),
            size=RenderSize(width=80, height=80),
            text="shit",
        )
        render_button.draw(draw_tool)
        # self.ui_manager.draw(draw_tool)
        # self.cursor.draw(draw_tool)

    def on_exit(self):
        print("=== 사용자 선택 화면 퇴장 ===")
        self.ui_manager.elements.clear()
        self.ui_manager.current_index = 0
        self.scroll_y = 0
