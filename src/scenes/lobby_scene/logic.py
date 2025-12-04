from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from classes.mushroom_class import MushroomType
from schemas.mushitroom_schema import MushitroomSchema
from settings.mushitroom_enums import SceneType
from utils.name_after_mushitroom import MushroomNameGenerator


if TYPE_CHECKING:
    from scenes.lobby_scene.scene import LobbyScene


# Scene 객체를 인자로 받아서 DB 작업을 수행합니다.
def check_and_initialize_user(scene: "LobbyScene"):
    """유저 접속 시 게임 상태 확인 및 초기화"""
    if not scene.user_id:
        print("[Error] user_id가 없습니다.")
        return

    game_state = scene.db.get_full_game_state(scene.user_id)
    if game_state is None:
        scene.db.save_game_state(user_id=scene.user_id, money=20, days=0)
        game_state = scene.db.get_full_game_state(scene.user_id)

    scene.game_state = game_state
    print(f"[System] 로비 데이터 로드 완료: {scene.user_id}")


def adopt_mushroom(scene: "LobbyScene"):
    """버섯 입양 로직"""
    print("🍄 버섯 입양 시도...")

    if scene.user_id is None:
        return

    # 살아있는 버섯 수 체크 (로직 분리)
    if scene.db.count_alive_mushrooms(scene.user_id) >= 3:
        print("⚠️ 버섯은 최대 3마리까지만 키울 수 있습니다.")
        return

    new_mush_id = str(uuid.uuid4())
    now_str = datetime.now().isoformat()

    new_mushroom = MushitroomSchema(
        user_id=scene.user_id,
        id=new_mush_id,
        created=now_str,
        type=MushroomType.GOMBO,
        name=MushroomNameGenerator().get_random_name(name=MushroomType.GOMBO.name_kr),
        age=0,
        exp=0,
        level=1,
        health=100,
        talent=5,
        cute=10,
        is_alive=True,
    )

    scene.db.save_mushitroom(user_id=scene.user_id, mush_data=new_mushroom)
    print("✅ 새 버섯 입양 완료!")

    # 로직 완료 후 UI 갱신 요청
    from .ui_builder import build_lobby_ui

    build_lobby_ui(scene)


def feed_mushroom(scene: "LobbyScene"):
    scene._scene_manager.switch_scene(SceneType.FEED_SCENE)
    pass
