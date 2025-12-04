from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.scenes.mushroom_select_scene import SelectMushroomScene


def initialize_user(scene: "SelectMushroomScene"):
    game_state = scene.db.get_full_game_state(scene._user_id)
    if game_state is None:
        scene.db.save_game_state(user_id=scene._user_id, money=20, days=0)
        game_state = scene.db.get_full_game_state(scene._user_id)

    scene._game_state = game_state
    print(f"[System] 로비 데이터 로드 완료: {scene._user_id}")

    pass
