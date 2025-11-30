from PIL.ImageDraw import ImageDraw
from src.settings.mushitroom_enums import FontStyle
from src.classes.render_coordinate import RenderCoordinate
from src.classes.render_size import RenderSize
from src.classes.render_object import RenderObject
from PIL import ImageFont

from utils.resource_loader import load_custom_font


class RenderText(RenderObject):
    text: str
    color: str
    _font: ImageFont.ImageFont | ImageFont.FreeTypeFont

    def __init__(
        self,
        coordinate: RenderCoordinate,
        text: str,
        size: RenderSize,
        font_size: int,
        font_style: FontStyle,
        color: str,
    ) -> None:
        super().__init__(coordinate, size)
        self._font = load_custom_font(
            path=f"./src/assets/fonts/{font_style.value}",
            size=font_size,
        )
        self.text = text
        self.color = color

    def update(self):
        return super().update()

    def draw(self, canvas: ImageDraw):
        half_width = self.size.width // 2
        half_height = self.size.height // 2
        top_left_x = self.coordinate.x - half_width
        top_left_y = self.coordinate.y - half_height
        canvas.text(
            font=self._font,
            xy=(
                top_left_x,
                top_left_y,
            ),
            text=self.text,
            fill=self.color,
            anchor="mm",
            align="center",
        )
