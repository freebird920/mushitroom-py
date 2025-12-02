from PIL.ImageDraw import ImageDraw
from settings.mushitroom_config import ZOOM_IN
from src.settings.mushitroom_enums import FontStyle
from src.classes.render_coordinate import RenderCoordinate
from src.classes.render_size import RenderSize
from src.classes.render_object import RenderObject
from PIL import ImageFont

from src.utils.resource_loader import load_custom_font


class RenderText(RenderObject):
    text: str
    color: str
    _font: ImageFont.ImageFont | ImageFont.FreeTypeFont

    def __init__(
        self,
        coordinate: RenderCoordinate,
        font_size: int,
        font_style: FontStyle,
        color: str = "black",
        text: str = "",
        size: RenderSize = RenderSize(0, 0),
    ) -> None:
        super().__init__(coordinate, size)
        self._font = load_custom_font(
            path=f"./src/assets/fonts/{font_style.value}",
            size=font_size * ZOOM_IN,
        )
        self.text = text
        self.color = color

    def update(self):
        return super().update()

    def draw(self, canvas: ImageDraw):

        canvas.text(
            font=self._font,
            xy=(
                self.coordinate.x,
                self.coordinate.y,
            ),
            text=self.text,
            fill=self.color,
            anchor="mm",
            align="center",
        )
