from typing import TYPE_CHECKING

from classes.mushroom_class import MushroomType
from utils.new_mushroom import new_mushroom


if TYPE_CHECKING:
    from src.scenes.mushroom_select_scene import SelectMushroomScene


def adopt_mushroom(scene: "SelectMushroomScene"):
    new_mushroom(
        user_id=scene._user_id,
        mushroom_type=MushroomType.get_random(),
    )
    scene.update()
    # 2. 순환 참조 방지를 위해 함수 안에서 import
    from scenes.mushroom_select_scene import ui_builder

    # 3. DB에서 최신 상태(버섯 리스트 포함) 다시 불러오기
    scene._game_state = scene.db.get_full_game_state(scene._user_id)

    # 4. 기존에 그려져 있던 버섯 이미지들 싹 지우기
    scene._mushroom_ui_manager.clear_components()

    # 5. 최신 데이터로 버섯 다시 그리기
    ui_builder.build_mushrooms(scene)


def initialize_user(scene: "SelectMushroomScene"):
    game_state = scene.db.get_full_game_state(scene._user_id)
    if game_state is None:
        scene.db.save_game_state(user_id=scene._user_id, money=20, days=0)
        game_state = scene.db.get_full_game_state(scene._user_id)

    scene._game_state = game_state
    print(f"[System] 로비 데이터 로드 완료: {scene._user_id}")

    pass
