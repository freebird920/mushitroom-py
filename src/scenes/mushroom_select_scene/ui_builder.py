from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.cursor_component import CursorComponent
from components.render_button import RenderButton
from components.render_ui_component import RenderUiComponent
from settings.mushitroom_config import CENTER_X, CENTER_Y
from settings.mushitroom_enums import FontStyle

if TYPE_CHECKING:
    from scenes.mushroom_select_scene.scene import SelectMushroomScene


def build_mushroom_select_scene_ui(scene: "SelectMushroomScene"):
    _ui_manager = scene._ui_manager
    _ui_manager.cursor = CursorComponent(
        coordinate=RenderCoordinate(0, 0), size=RenderSize(100, 50)
    )

    # buttons
    adopt_button = RenderButton(
        coordinate=RenderCoordinate(CENTER_X, CENTER_Y),
        size=RenderSize(100, 30),
        font_size=10,
        font_style=FontStyle.COOKIE_BOLD,
        text="ADOPT",
    )
    adopt_button_component = RenderUiComponent(
        render_object=adopt_button,
        on_activate=None,
        is_selectable=True,
    )
    _ui_manager.add_component(adopt_button_component)
