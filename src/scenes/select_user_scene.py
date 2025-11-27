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
        
        # --- 스크롤 설정을 위한 변수들 ---
        self.scroll_y = 0  # 현재 스크롤된 양
        self.list_start_y = 60  # 리스트가 시작되는 Y 위치
        self.item_height = 50   # 각 버튼의 높이 + 간격
        # 화면의 높이 (manager에 screen_height가 있다고 가정하거나 상수로 지정)
        # 예: 전체 600px 중 하단 여백 등을 뺀 리스트가 보일 수 있는 최대 높이 설정
        self.visible_height = 400 

    def on_enter(self):
        print("=== 사용자 선택 화면 진입 ===")
        self.ui_manager.elements.clear()
        self.scroll_y = 0 # 스크롤 초기화

        # DB에서 유저 조회
        self.users = self.db.get_all_users()

        # 1. 고정 타이틀 (스크롤 영향을 받지 않음)
        title = MushitroomInterfaceObject(
            index=-1, # 선택 불가능하도록 -1
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

        # 2. 유저 목록 버튼 생성
        # Y좌표는 나중에 update()에서 계산하므로 여기선 초기 순서만 중요함
        for i, user in enumerate(self.users):
            btn = MushitroomInterfaceObject(
                index=i,
                x=80,
                y=self.list_start_y + (i * self.item_height), # 초기 위치
                width=200,
                height=40,
                color="#DDDDDD",
                text=f"{user.username}",
                font_weight=FontWeight.REGULAR,
                on_action=lambda u=user: self.select_user(u),
            )
            self.ui_manager.add_element(btn)

        # 3. 새 유저 생성 버튼
        new_user_index = len(self.users)
        btn_create = MushitroomInterfaceObject(
            index=new_user_index,
            x=80,
            y=self.list_start_y + (new_user_index * self.item_height), # 초기 위치
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
        # self.manager.switch_scene(...)
        pass

    def create_new_user(self):
        print("새 유저 생성")
        self.db.create_user(f"{NameGenerator().get_random_name()}")
        self.on_enter()

    def handle_input(self, input_state: "InputState"):
        just_pressed = input_state.just_pressed_keys

        if "bracketleft" in just_pressed or "q" in just_pressed:
            self.ui_manager.select_prev()
        
        if "bracketright" in just_pressed or "e" in just_pressed:
            self.ui_manager.select_next()

        if "Return" in just_pressed:
            current_btn = self.ui_manager.elements[self.ui_manager.current_index]
            # 타이틀(index=-1)이 선택되는 것을 방지
            if self.ui_manager.current_index >= 0 and current_btn.on_action:
                current_btn.on_action()

    def update(self):
        # === 스크롤 로직 핵심 ===
        
        # 1. 현재 선택된 인덱스 가져오기
        current_idx = self.ui_manager.current_index
        
        # 타이틀(-1)이 선택되어 있다면 스크롤 계산 건너뜀
        if current_idx < 0:
            return

        # 2. 선택된 아이템의 '원래' Y 위치 계산 (스크롤 적용 전 절대 위치)
        target_y = self.list_start_y + (current_idx * self.item_height)
        
        # 3. 스크롤 범위 계산 (Camera Logic)
        # 선택된 아이템이 화면 위로 나갔다면? -> 스크롤을 줄여서 위를 보여줌
        if target_y < self.list_start_y + self.scroll_y:
            self.scroll_y = target_y - self.list_start_y
            
        # 선택된 아이템이 화면 아래로 나갔다면? -> 스크롤을 늘려서 아래를 보여줌
        # (self.visible_height - self.item_height)는 화면의 바닥 기준선
        elif target_y > self.list_start_y + self.scroll_y + self.visible_height - self.item_height:
            self.scroll_y = target_y - (self.list_start_y + self.visible_height - self.item_height)

        # 4. 모든 UI 요소의 위치 업데이트
        for elem in self.ui_manager.elements:
            # 타이틀(index=-1)은 고정 (스크롤 안 함)
            if elem.index == -1:
                continue
            
            # 리스트 아이템들의 원래 위치 계산
            original_y = self.list_start_y + (elem.index * self.item_height)
            
            # 스크롤 오프셋 적용 (위로 밀어올리기 위해 뺌)
            elem.y = original_y - self.scroll_y

            # (선택 사항) 화면 밖의 요소는 그리지 않게 하거나 투명하게 처리하고 싶다면 여기서 처리
            # 예: 화면 밖 요소는 visible=False 처리 등
            # if elem.y < self.list_start_y or elem.y > self.list_start_y + self.visible_height:
            #     elem.visible = False # 만약 객체에 visible 속성이 있다면
            # else:
            #     elem.visible = True

    def draw(self, draw_tool):
        # 필요하다면 배경이나 리스트 영역 박스를 먼저 그림
        
        # UI 매니저가 그리기
        self.ui_manager.draw(draw_tool)
        
        # (옵션) 스크롤바 그리기
        # 리스트가 길 때만 우측에 현재 위치를 나타내는 바를 그려줄 수 있습니다.