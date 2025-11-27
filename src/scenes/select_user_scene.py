from typing import TYPE_CHECKING
from src.classes.scene_base import BaseScene
from src.classes.mushitroom_interface_object import (
    MushitroomInterfaceGroup,
    MushitroomInterfaceObject,
)
from src.settings.mushitroom_enums import FontWeight
from src.utils.name_generator import NameGenerator

if TYPE_CHECKING:
    from classes.input_manager import InputState


class SelectUserScene(BaseScene):
    def __init__(self, manager, db):
        super().__init__(manager)
        self.db = db
        self.ui_manager = MushitroomInterfaceGroup()
        self.users = []

    def on_enter(self):
        print("=== 사용자 선택 화면 진입 ===")
        self.ui_manager.elements.clear()

        # DB에서 유저 조회
        self.users = self.db.get_all_users()

        # 타이틀
        title = MushitroomInterfaceObject(
            index=-1,
            x=80,
            y=10,
            width=200,
            height=30,
            color="black",
            text="SELECT USER",
            font_weight=FontWeight.HEAVY,
            text_color="white",
        )
        self.ui_manager.add_element(title)

        # 유저 목록 버튼 생성
        start_y = 60
        for i, user in enumerate(self.users):
            btn = MushitroomInterfaceObject(
                index=i,  # 네비게이션 순서
                x=80,
                y=start_y + (i * 50),
                width=200,
                height=40,
                color="#DDDDDD",
                text=f"{user.username}",
                font_weight=FontWeight.REGULAR,
                # 선택 시 실행할 함수 (lambda로 감싸서 user 객체 전달)
                on_action=lambda u=user: self.select_user(u),
            )
            self.ui_manager.add_element(btn)

        # 새 유저 생성 버튼 (맨 아래)
        new_user_index = len(self.users)
        btn_create = MushitroomInterfaceObject(
            index=new_user_index,
            x=80,
            y=start_y + (len(self.users) * 50) + 20,
            width=200,
            height=40,
            color="#AAAAFF",
            text="+ NEW USER",
            font_weight=FontWeight.HEAVY,
            on_action=self.create_new_user,
        )
        self.ui_manager.add_element(btn_create)

    def select_user(self, user):
        print(f"유저 선택됨: {user.username}")
        # 순환 참조 방지를 위해 메서드 내부에서 임포트
        # from src.scenes.main_game_scene import MainGameScene

        # self.manager.switch_scene(MainGameScene(self.manager, user))
        pass

    def create_new_user(self):
        print("새 유저 생성")

        self.db.create_user(f"{NameGenerator().get_random_name()}")
        self.on_enter()  # 목록 새로고침

    def handle_input(self, input_state: "InputState"):
        # UI 네비게이션: '한 번 클릭'에 반응해야 하므로 just_pressed_keys를 확인합니다.
        # InputManager의 key_map에 정의된 실제 키 이름들을 확인합니다.

        just_pressed = input_state.just_pressed_keys

        # 이전(위/왼쪽) 선택: '[' 키 또는 'q' 키
        if "bracketleft" in just_pressed or "q" in just_pressed:
            self.ui_manager.select_prev()

        # 다음(아래/오른쪽) 선택: ']' 키 또는 'e' 키
        if "bracketright" in just_pressed or "e" in just_pressed:
            self.ui_manager.select_next()

        # 선택(엔터): Enter 키
        if "Return" in just_pressed:
            # 현재 선택된 UI 요소의 액션 실행
            current_btn = self.ui_manager.elements[self.ui_manager.current_index]
            if current_btn.on_action:
                current_btn.on_action()

    def update(self):
        pass

    def draw(self, draw_tool):
        self.ui_manager.draw(draw_tool)
