import random
from typing import TYPE_CHECKING, TypedDict, Unpack, List

from PIL.ImageDraw import ImageDraw

from src.classes.mushitroom_interface_object import (
    MushitroomInterfaceGroup,
    MushitroomInterfaceObject,
)
from src.settings import mushitroom_config
from src.classes.scene_base import BaseScene
from src.classes.mushitroom_png_object import PngObject
from src.settings.mushitroom_enums import InputActions, ObjectType, SceneType


if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from src.managers.scene_manager import SceneManager
    from src.schemas.user_schema import User
    from src.services.sq_service import SqService


class UserSceneArgs(TypedDict):
    user: "User"


class UserTestScene(BaseScene):
    player: PngObject
    obstacles: List[PngObject]
    spawn_timer: int
    score: int
    ui_group: MushitroomInterfaceGroup
    # 물리 엔진 상수
    GRAVITY = 1.5
    INITIAL_VELOCITY = 2
    user: "User | None"

    def __init__(
        self,
    ):

        super().__init__()
        self.score = 0
        # 1. 플레이어 설정
        self.ui_group = MushitroomInterfaceGroup()
        self.player = PngObject(
            x=100,
            y=200,
            width=30,
            height=30,
            color="red",
            object_type=ObjectType.DEFAULT,
            href="./src/assets/images/magui3.png",
        )

        # 2. 장애물 변수 초기화
        self.obstacles = []
        self.spawn_timer = 0
        self.score_ui = MushitroomInterfaceObject(
            index=0,
            x=100,
            y=10,
            width=100,
            height=10,
            color="white",
            text=f"{self.score}",
            text_color="black",
        )
        self.user_name_ui = MushitroomInterfaceObject(
            index=0,
            x=200,
            y=10,
            width=100,
            height=10,
            color="white",
            text="",
            text_color="black",
        )

        self.ui_group.add_element(self.score_ui)

    def on_enter(self, **kwargs: Unpack[UserSceneArgs]):  # type: ignore[override]
        super().on_enter()
        if kwargs.get("user"):
            self.user = kwargs["user"]
            print(f"유저: {self.user.username}")
            self.user_name_ui.text = self.user.username
        # 씬 재진입 시 장애물 초기화 (선택사항)
        self.ui_group.add_element(self.user_name_ui)
        self.obstacles.clear()

    # ---------------------------------------------------------
    # 1. 입력 처리 (User Input)
    # ---------------------------------------------------------
    def handle_input(self, input_state: "InputState"):
        super().handle_input(input_state)

        step = 10

        # 씬 전환
        if InputActions.ENTER in input_state.just_pressed_actions:
            self.manager.switch_scene(SceneType.SELECT_USER)

        # 플레이어 이동 (화면 밖으로 나가지 않게 제한)
        if "Up" in input_state.pressed_keys:
            self.player.y = max(0, self.player.y - step)

        if "Down" in input_state.pressed_keys:
            self.player.y = min(
                mushitroom_config.DISPLAY_HEIGHT - self.player.height,
                self.player.y + step,
            )

        if "Left" in input_state.pressed_keys:
            self.player.x = max(0, self.player.x - step)

        if "Right" in input_state.pressed_keys:
            self.player.x = min(
                mushitroom_config.DISPLAY_WIDTH - self.player.width,
                self.player.x + step,
            )

    # ---------------------------------------------------------
    # 2. 게임 로직 업데이트
    # ---------------------------------------------------------
    def update(self):

        # super().update()

        # A. 장애물 스폰 로직
        self.spawn_timer += 1
        if self.spawn_timer > 10:
            self.spawn_obstacle()
            self.spawn_timer = 0

        # B. 장애물 물리 이동 및 충돌 처리
        # 리스트 복사본[:]을 사용하여 안전하게 순회
        for obstacle in self.obstacles[:]:
            # 1. 중력 적용 (속도 증가)
            obstacle.velocity_y += self.GRAVITY

            # 2. 위치 이동
            obstacle.y += int(obstacle.velocity_y)

            # 3. 화면 밖 제거 (메모리 관리)
            if obstacle.y > mushitroom_config.DISPLAY_HEIGHT:
                self.obstacles.remove(obstacle)
                self.score = self.score + 1
                continue

            # 4. 충돌 체크 (게임 오버)
            if self.check_collision(self.player, obstacle):
                print(f"게임 오버! 충돌 발생 (장애물 Y: {obstacle.y})")
                self.manager.switch_scene(SceneType.SELECT_USER)
                return
        self.score_ui.text = f"{self.score}"

    def spawn_obstacle(self):
        """장애물 생성 및 초기 속도 설정"""
        random_x = random.randint(0, mushitroom_config.DISPLAY_WIDTH - 30)

        new_obstacle = PngObject(
            x=random_x,
            y=-30,
            width=30,
            height=30,
            color="blue",
            object_type=ObjectType.DEFAULT,
            href="./src/assets/images/tong3.png",
        )
        # 동적 속성 추가: 초기 속도
        new_obstacle.velocity_y = self.INITIAL_VELOCITY

        self.obstacles.append(new_obstacle)

    def check_collision(self, obj1: PngObject, obj2: PngObject) -> bool:
        """AABB 충돌 감지"""
        l1, r1 = obj1.x, obj1.x + obj1.width
        t1, b1 = obj1.y, obj1.y + obj1.height

        l2, r2 = obj2.x, obj2.x + obj2.width
        t2, b2 = obj2.y, obj2.y + obj2.height

        if r1 < l2 or l1 > r2 or b1 < t2 or t1 > b2:
            return False
        return True

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self.ui_group.draw(draw_tool)
        self.player.draw(draw_tool)
        for obstacle in self.obstacles:
            obstacle.draw(draw_tool)
