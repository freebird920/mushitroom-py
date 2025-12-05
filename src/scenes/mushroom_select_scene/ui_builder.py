from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.cursor_component import CursorComponent
from components.mushroom_component import MushroomComponent
from components.render_button import RenderButton
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent
from scenes.mushroom_select_scene import logic
from settings.mushitroom_config import CENTER_X, CENTER_Y
from settings.mushitroom_enums import FontStyle

if TYPE_CHECKING:
    from scenes.mushroom_select_scene.scene import SelectMushroomScene


def build_mushrooms(scene: "SelectMushroomScene") -> None:
    if scene._game_state is None or scene._game_state.mushitrooms is None:
        print("NO MUSHIT ROOMS")
        return

    for index, mushit_id in enumerate(scene._game_state.mushitrooms):
        print(index)
        mushit_info = scene.db.get_mushitroom(mushit_id)
        if mushit_info is None or mushit_info.type is None:
            return print("NO MUSHIT INFO")
        mushit_position_x = CENTER_X
        if index == 0:
            mushit_position_x = CENTER_X
        elif index == 1:
            mushit_position_x = CENTER_X - (CENTER_X // 2)
        elif index == 2:
            mushit_position_x = CENTER_X + (CENTER_X // 2)
        mushit_position = RenderCoordinate(
            mushit_position_x,
            CENTER_Y - (CENTER_Y // 3),
        )
        mushit_img = MushroomComponent(
            mushroom_type=mushit_info.type,
            coordinate=mushit_position,
            size=RenderSize(50, 50),
        )
        mushit_ui_comp = RenderUiComponent(
            render_object=mushit_img.mushroom_images[0],
            is_selectable=True,
            on_activate=None,
        )
        mushit_name_text = RenderText(
            text=mushit_info.name,
            coordinate=RenderCoordinate(mushit_position.x, mushit_position.y + 50),
            font_size=10,
            font_style=FontStyle.COOKIE_BOLD,
        )
        mushit_name_comp = RenderUiComponent(
            render_object=mushit_name_text,
        )
        scene._mushroom_ui_manager.add_component(mushit_name_comp)
        scene._mushroom_ui_manager.add_component(mushit_ui_comp)
        pass
    return scene.update()


def build_mushroom_select_scene_ui(scene: "SelectMushroomScene"):
    _ui_manager = scene._ui_manager
    _ui_manager.cursor = CursorComponent(
        coordinate=RenderCoordinate(0, 0),
        size=RenderSize(320 // 3, 100 // 3),
    )

    # buttons
    adopt_button = RenderButton(
        coordinate=RenderCoordinate(CENTER_X, CENTER_Y + (CENTER_Y // 2)),
        size=RenderSize(320 // 3, 100 // 3),
        font_size=14,
        font_style=FontStyle.COOKIE_BOLD,
        text="ADOPT",
    )
    adopt_button_component = RenderUiComponent(
        render_object=adopt_button,
        on_activate=lambda: logic.adopt_mushroom(scene=scene),
        is_selectable=True,
    )
    _ui_manager.add_component(adopt_button_component)
