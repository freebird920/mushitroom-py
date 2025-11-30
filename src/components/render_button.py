# import from external
from PIL.ImageDraw import ImageDraw

# import settings
from src.settings.mushitroom_enums import FontStyle

# import components
from src.components.render_text import RenderText
from src.components.render_image import RenderImage

# import classes
from src.classes.render_coordinate import RenderCoordinate
from src.classes.render_size import RenderSize
from src.classes.render_object import RenderObject


class RenderButton(RenderObject):

    _render_button_image: RenderImage
    render_text: RenderText

    def __init__(
        self,
        coordinate: RenderCoordinate,
        size: RenderSize,
        font_style: FontStyle = FontStyle.COOKIE_BOLD,
        text_color: str = "black",
        font_size: int = 15,
        text: str = "",
    ) -> None:
        super().__init__(coordinate, size)
        self.render_text = RenderText(
            coordinate=self.coordinate,
            text=text,
            font_size=font_size,
            size=self.size,
            font_style=font_style,
            color=text_color,
        )
        self._render_button_image = RenderImage(
            coordinate=self.coordinate,
            size=self.size,
            src="./src/assets/images/button.png",
        )

    def draw(self, canvas: ImageDraw):
        self._render_button_image.draw(canvas)
        self.render_text.draw(canvas)
