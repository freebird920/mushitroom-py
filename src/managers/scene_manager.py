from enum import Enum, auto
from typing import TYPE_CHECKING, Dict, Type, Optional


# 순환 참조(Circular Import) 방지를 위한 타입 힌팅용 임포트
from src.settings.mushitroom_enums import SceneType

if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from src.classes.scene_base import BaseScene
    from services.sq_service import SqService


# 1. 씬의 종류를 정의하는 Enum (자동 번호 할당)


class SceneManager:
    # 타입 힌트 (명찰 달기)
    db: "SqService"
    current_scene: Optional["BaseScene"]
    scene_cache: Dict[SceneType, "BaseScene"]
    scene_registry: Dict[SceneType, Type["BaseScene"]]

    def __init__(self, db_instance: "SqService"):
        self.db = db_instance
        self.current_scene = None

        # [핵심 1] 씬 인스턴스를 저장해두는 금고 (캐시)
        # 한 번 만든 씬은 여기에 저장해두고 계속 꺼내 씁니다.
        self.scene_cache = {}

        # [핵심 2] Enum과 실제 클래스를 연결하는 등록부
        # 주의: 여기서 import 하는 이유는 순환 참조 에러를 막기 위함입니다.
        # (SceneManager가 실행될 때 비로소 Scene 클래스들을 불러옵니다)
        from src.scenes.select_user_scene import SelectUserScene
        from src.scenes.user_test_scene import UserTestScene
        from src.scenes.phishing_test_scene import PhishingTestScene

        self.scene_registry = {
            SceneType.SELECT_USER: SelectUserScene,
            SceneType.USER_TEST: UserTestScene,
            SceneType.PHISHING: PhishingTestScene,
        }

    def switch_scene(self, scene_type: SceneType, **kwargs):
        """
        씬을 전환합니다.
        :param scene_type: 이동할 씬의 Enum 타입
        :param kwargs: 다음 씬의 on_enter로 넘겨줄 데이터 (예: user=player1)
        """

        # 1. 캐시에 씬이 없으면 생성 (Lazy Loading)
        if scene_type not in self.scene_cache:
            if scene_type not in self.scene_registry:
                print(f"[Error] {scene_type} 은(는) 레지스트리에 등록되지 않았습니다!")
                return

            # 클래스 가져오기
            scene_class = self.scene_registry[scene_type]

            # 인스턴스 생성 (__init__ 실행) 및 캐시 저장
            # 여기서 self(매니저)와 db를 주입합니다.
            print(f"[System] 씬 최초 생성: {scene_type}")
            self.scene_cache[scene_type] = scene_class(self, self.db)

        # 2. 캐시에서 인스턴스 꺼내기
        next_scene = self.scene_cache[scene_type]

        # 3. 현재 씬 정리 (Exit)
        if self.current_scene:
            self.current_scene.on_exit()

        # 4. 씬 교체
        self.current_scene = next_scene

        # 5. [핵심 3] 새 씬 진입 및 데이터 주입 (Enter + Data)
        # **kwargs가 딕셔너리를 풀어서 on_enter(user=..., level=...) 형태로 넣어줍니다.
        # 여기서 씬 내부 변수(점수, 위치 등)가 초기화되어야 합니다.
        self.current_scene.on_enter(**kwargs)

    def handle_input(self, input_state: "InputState"):
        if self.current_scene:
            self.current_scene.handle_input(input_state)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, draw_tool):
        if self.current_scene:
            self.current_scene.draw(draw_tool)

    # (옵션) 프로그램을 완전히 종료할 때 호출
    def quit(self):
        if self.current_scene:
            self.current_scene.on_exit()
