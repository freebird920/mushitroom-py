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

    def __init__(
        self,
        coordinate: RenderCoordinate,
        size: RenderSize,
        font_style: FontStyle = FontStyle.COOKIE_BOLD,
        text_color: str = "black",
        font_size: int = 15,
        text: str = "",
    ) -> None:
        # 1. 부모 init 호출 (self.coordinate와 self.size는 물리적(2배) 크기가 됨)
        super().__init__(coordinate, size)

        # [핵심 수정] 자식(이미지, 텍스트)에게 좌표를 넘길 때 주의할 점!
        # 1) 자식들은 'Center' 좌표를 기준으로 그립니다.
        # 2) 자식들도 RenderObject이므로, 입력받은 좌표를 또 2배(Zoom) 합니다.
        # 따라서, '논리적(1배) 크기의 중앙 좌표'를 계산해서 넘겨줘야 합니다.

        # 논리적 중앙 좌표 계산
        center_x = coordinate.x + (size.width // 2)
        center_y = coordinate.y + (size.height // 2)
        logical_center = RenderCoordinate(center_x, center_y)

        # 자식 생성 (논리적 중앙 좌표 전달 -> 자식이 알아서 2배 확대 -> 물리적 중앙에 배치됨)
        # 더블 줌 문제 해결됨
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
            src="./src/assets/images/button.png",
        )

    def draw(self, canvas: ImageDraw):
        self._render_button_image.draw(canvas)
        self._render_text.draw(canvas)
