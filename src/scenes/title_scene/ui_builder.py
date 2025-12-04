from typing import Callable, List, Optional
from classes.mushroom_class import MushroomType
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.mushroom_component import MushroomComponent
from components.render_button import RenderButton
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent
from managers.scene_manager import SceneManager
from settings.mushitroom_config import CENTER_X, CENTER_Y
from settings.mushitroom_enums import FontStyle


class TitleSceneUiBuilder:
    _scene_manager: SceneManager
    _title_text_component: RenderUiComponent
    _busots: List[MushroomComponent]

    def __init__(self) -> None:
        self._scene_manager = SceneManager()
        title_text_y = CENTER_Y - (CENTER_Y // 3)
        self._title_text_component = RenderUiComponent(
            render_object=RenderText(
                coordinate=RenderCoordinate(x=CENTER_X, y=title_text_y),
                size=RenderSize(0, 0),
                font_size=42,
                color="black",
                font_style=FontStyle.COOKIE_BOLD,
                text="니얼굴윤겔라",
            ),
            is_selectable=False,
            on_activate=None,
        )
        self.buttons: List[RenderUiComponent] = [
            RenderUiComponent(
                render_object=RenderButton(
                    coordinate=RenderCoordinate(CENTER_X // 2, CENTER_Y),
                    size=RenderSize(100, 30),
                    text="START",
                ),
            )
        ]
        mushroom_size = 30
        mushroom_y = title_text_y - 30
        self._busots = [
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X - (CENTER_X // 4 * 3), mushroom_y),
                mushroom_type=MushroomType.SALGU,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X - (CENTER_X // 4 * 2), mushroom_y),
                mushroom_type=MushroomType.GWANG,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X - (CENTER_X // 4 * 1), mushroom_y),
                mushroom_type=MushroomType.DALGYAL,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X, mushroom_y),
                mushroom_type=MushroomType.MAGUI,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X + (CENTER_X // 4 * 1), mushroom_y),
                mushroom_type=MushroomType.GOMBO,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X + (CENTER_X // 4 * 2), mushroom_y),
                mushroom_type=MushroomType.SASUM,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
            MushroomComponent(
                coordinate=RenderCoordinate(CENTER_X + (CENTER_X // 4 * 3), mushroom_y),
                mushroom_type=MushroomType.HWANGUM,
                size=RenderSize(mushroom_size, mushroom_size),
            ),
        ]

        pass

    def build_buttons(
        self,
        on_start: Optional[Callable[[], None]],
        on_exit: Optional[Callable[[], None]],
    ) -> List[RenderUiComponent]:
        result: List[RenderUiComponent] = [
            # 1. START 버튼
            RenderUiComponent(
                is_selectable=True,
                on_activate=on_start,
                render_object=RenderButton(
                    coordinate=RenderCoordinate(CENTER_X, CENTER_Y + 50),  # 위치 조정
                    size=RenderSize(100, 30),
                    text="START",
                ),
            ),
            # 2. EXIT 버튼
            RenderUiComponent(
                is_selectable=True,
                on_activate=on_exit,
                render_object=RenderButton(
                    coordinate=RenderCoordinate(
                        CENTER_X, CENTER_Y + 100
                    ),  # START보다 아래로
                    size=RenderSize(100, 30),
                    text="EXIT",
                ),
            ),
        ]
        return result

    def build_components(self) -> List[RenderUiComponent]:
        result: List[RenderUiComponent] = [self._title_text_component]

        for bs in self._busots:
            initial_image = bs.mushroom_images[bs.mushroom_direction - 1]

            ui_comp = RenderUiComponent(
                render_object=initial_image,
                is_selectable=False,
                on_activate=None,
            )

            result.append(ui_comp)

        return result
