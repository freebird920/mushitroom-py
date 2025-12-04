from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.mushroom_component import MushroomComponent
from classes.mushroom_class import MushroomType
from components.render_ui_component import RenderUiComponent
from components.render_text import RenderText
from components.render_image import RenderImage
from settings.mushitroom_config import CENTER_X
from settings.mushitroom_enums import FontStyle

if TYPE_CHECKING:

    from scenes.lobby_scene.scene import LobbyScene


def build_lobby_ui(scene: "LobbyScene"):
    """로비 씬의 모든 UI 컴포넌트를 생성하고 배치합니다."""
    scene.ui_component_manager.clear_components(reset_index=False)

    scene.bussot_component = MushroomComponent(
        mushroom_type=MushroomType.MAGUI,
        coordinate=RenderCoordinate(50, 50),
        size=RenderSize(50, 50),
    )
    scene.anim_index = 0
    scene.bussot_ui_component = RenderUiComponent(
        is_selectable=False,
        render_object=scene.bussot_component.mushroom_images[scene.anim_index],
    )
    scene.ui_component_manager.add_component(scene.bussot_ui_component)

    # 2. 유저 ID 텍스트
    user_id_text = RenderText(
        coordinate=RenderCoordinate(CENTER_X, 10),
        color="black",
        text=f"{scene.user_id}",
        size=RenderSize(0, 0),
        font_size=12,
        font_style=FontStyle.COOKIE_BOLD,
    )
    scene.ui_component_manager.add_component(
        RenderUiComponent(is_selectable=False, render_object=user_id_text)
    )

    # 3. 보유 버섯 목록 표시
    _build_mushroom_list(scene)

    # 4. 하단 버튼 배치
    _build_bottom_buttons(scene)


def _build_mushroom_list(scene: "LobbyScene"):
    if scene.user_id is None:
        return

    my_mushrooms = scene.db.get_user_mushrooms(scene.user_id)
    start_y = 60
    gap_y = 30

    if not my_mushrooms:
        scene.ui_component_manager.add_component(
            RenderUiComponent(
                is_selectable=False,
                render_object=RenderText(
                    font_size=12,
                    font_style=FontStyle.COOKIE_BOLD,
                    color="black",
                    text="버섯이 없습니다.",
                    coordinate=RenderCoordinate(CENTER_X, 100),
                ),
            )
        )
    else:
        for i, mush in enumerate(my_mushrooms):
            display_text = f"{i+1}. {mush.name} (Lv.{mush.level})"
            scene.ui_component_manager.add_component(
                RenderUiComponent(
                    is_selectable=False,
                    render_object=RenderText(
                        font_size=10,
                        font_style=FontStyle.COOKIE_BOLD,
                        color="black",
                        text=display_text,
                        coordinate=RenderCoordinate(CENTER_X, start_y + (i * gap_y)),
                    ),
                )
            )


def _build_bottom_buttons(scene: "LobbyScene"):
    btn_y_pos = 200
    btn_x_start = 60
    btn_gap = 80

    # 입양 버튼
    adopt_button = RenderImage(
        coordinate=RenderCoordinate(btn_x_start, btn_y_pos),
        size=RenderSize(320 // 4, 100 // 4),
        src="./src/assets/images/btn_adopt.png",
    )

    # 입양 가능 여부 체크
    is_adoptable = False
    if scene.user_id and scene.db.count_alive_mushrooms(scene.user_id) < 3:
        is_adoptable = True

    scene.ui_component_manager.add_component(
        RenderUiComponent(
            is_selectable=is_adoptable,
            # scene에 정의된 래퍼 메서드를 호출하거나 logic 함수를 직접 연결
            on_activate=scene.handle_adopt,
            render_object=adopt_button,
        )
    )

    # 춤추기 버튼
    dance_button = RenderImage(
        coordinate=RenderCoordinate(btn_x_start + btn_gap, btn_y_pos),
        size=RenderSize((320 // 4), (100 // 4)),
        src="./src/assets/images/btn_dance.png",
    )
    scene.ui_component_manager.add_component(
        RenderUiComponent(
            is_selectable=True,
            on_activate=lambda: print("춤추기!"),
            render_object=dance_button,
        )
    )

    # 보급 버튼
    supply_button = RenderImage(
        coordinate=RenderCoordinate(btn_x_start + (btn_gap * 2), btn_y_pos),
        size=RenderSize(320 // 4, 100 // 4),
        src="./src/assets/images/btn_supply.png",
    )
    scene.ui_component_manager.add_component(
        RenderUiComponent(
            is_selectable=True,
            on_activate=scene.handle_feed,
            render_object=supply_button,
        )
    )
