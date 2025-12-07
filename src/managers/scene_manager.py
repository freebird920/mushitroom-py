from typing import TYPE_CHECKING, Dict, Type, Optional

# 순환 참조(Circular Import) 방지를 위한 타입 힌팅용 임포트
from settings.mushitroom_enums import SceneType
from managers.sq_manager import SqManager

if TYPE_CHECKING:
    from classes.scene_base import BaseScene


class SceneManager:
    # [Singleton 1] 인스턴스를 담을 클래스 변수
    _instance: Optional["SceneManager"] = None

    # 타입 힌트
    db: "SqManager"
    current_scene: Optional["BaseScene"]
    scene_cache: Dict[SceneType, "BaseScene"]
    scene_registry: Dict[SceneType, Type["BaseScene"]]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    # [Singleton 3] 초기화 제어 (최초 1회만 실행)
    # db_instance를 Optional로 변경했습니다. (두 번째 호출부터는 안 넣어도 되게 하려고)
    def __init__(self):
        # 이미 초기화되었다면 그냥 리턴 (재초기화 방지)
        if hasattr(self, "initialized"):
            return

        print("[System] SceneManager 초기화 (Singleton)")

        # 최초 생성 시 DB 인스턴스는 필수입니다.
        self.db = SqManager()
        self.current_scene = None
        self.scene_cache = {}

        # [핵심 2] Enum과 실제 클래스를 연결하는 등록부
        # 순환 참조 방지를 위한 내부 import 유지
        from scenes.select_user_scene import SelectUserScene
        from scenes.lobby_scene.scene import LobbyScene
        from scenes.title_scene.scene import TitleScene
        from scenes.feed_scene.scene import FeedScene
        from scenes.mushroom_select_scene import SelectMushroomScene
        from scenes.goeha_scene import GoehaScene

        self.scene_registry = {
            SceneType.SELECT_USER: SelectUserScene,
            SceneType.LOBBY_SCENE: LobbyScene,
            SceneType.TITLE_SCENE: TitleScene,
            SceneType.FEED_SCENE: FeedScene,
            SceneType.SELECT_MUSHROOM: SelectMushroomScene,
            SceneType.GOEHA_TIME: GoehaScene,
        }

        self.initialized = True

    def switch_scene(self, scene_type: SceneType, **kwargs):
        """
        씬을 전환합니다.
        :param scene_type: 이동할 씬의 Enum 타입
        :param kwargs: 다음 씬의 on_enter로 넘겨줄 데이터
        """
        # 1. 캐시에 씬이 없으면 생성 (Lazy Loading)
        if scene_type not in self.scene_cache:
            if scene_type not in self.scene_registry:
                print(f"[Error] {scene_type} 은(는) 레지스트리에 등록되지 않았습니다!")
                return

            # 클래스 가져오기
            scene_class = self.scene_registry[scene_type]

            # 인스턴스 생성 (__init__ 실행) 및 캐시 저장
            print(f"[System] 씬 최초 생성: {scene_type}")
            self.scene_cache[scene_type] = scene_class()

        # 2. 캐시에서 인스턴스 꺼내기
        next_scene = self.scene_cache[scene_type]

        # 3. 현재 씬 정리 (Exit)
        if self.current_scene:
            self.current_scene.on_exit()

        # 4. 씬 교체
        self.current_scene = next_scene

        # 5. 새 씬 진입 및 데이터 주입 (Enter + Data)
        self.current_scene.on_enter(**kwargs)

    def handle_input(self):
        if self.current_scene:
            self.current_scene.handle_input()

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, draw_tool):
        if self.current_scene:
            self.current_scene.draw(draw_tool)

    def quit(self):
        if self.current_scene:
            self.current_scene.on_exit()
