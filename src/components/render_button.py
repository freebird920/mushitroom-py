# import from external
from PIL.ImageDraw import ImageDraw

# import settings
from settings.mushitroom_enums import FontStyle

# import components
from components.render_text import RenderText
from components.render_image import RenderImage

# import classes
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.render_object import RenderObject


class RenderButton(RenderObject):

    _render_button_image: RenderImage
    _render_text: RenderText
    _img_src: str

    def __init__(
        self,
        coordinate: RenderCoordinate,
        size: RenderSize,
        font_style: FontStyle = FontStyle.COOKIE_BOLD,
        text_color: str = "black",
        font_size: int = 15,
        text: str = "",
        img_src: str = "./src/assets/images/button.png",
    ) -> None:
        # 1. 부모 init 호출 (self.coordinate와 self.size는 물리적(2배) 크기가 됨)
        super().__init__(coordinate, size)
        self._img_src = img_src
        self._render_text = RenderText(
            coordinate=coordinate,
            text=text,
            font_size=font_size,
            size=size,
            font_style=font_style,
            color=text_color,
        )
        self._render_button_image = RenderImage(
            coordinate=coordinate,
            size=size,
            src=self._img_src,
        )

    def draw(self, canvas: ImageDraw):
        self._render_button_image.draw(canvas)
        self._render_text.draw(canvas)
