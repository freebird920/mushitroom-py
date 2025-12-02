import time
import math
from typing import TYPE_CHECKING
from src.classes.render_coordinate import RenderCoordinate
from src.classes.render_object import RenderObject
from src.classes.render_size import RenderSize
from src.components.render_image import RenderImage

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class CursorComponent(RenderObject):
    _cursor_hat: RenderImage
    _cursor_ring: RenderImage

    # 애니메이션 설정
    _bounce_amplitude: int = 5  # 위아래로 움직이는 범위 (픽셀)

    def __init__(self, coordinate: RenderCoordinate, size: RenderSize) -> None:
        super().__init__(coordinate, size)

        ring_width = size.width
        ring_height = size.height

        hat_width = ring_width
        hat_height = int(ring_height / 3)

        ring_x = coordinate.x
        ring_y = coordinate.y

        hat_x = coordinate.x
        hat_y = ring_y - (ring_height // 2) - (hat_height // 2)

        self._cursor_hat = RenderImage(
            coordinate=RenderCoordinate(hat_x, hat_y),
            size=RenderSize(hat_width, hat_height),
            src="./src/assets/images/cursor_hat.png",
        )

        self._cursor_ring = RenderImage(
            coordinate=RenderCoordinate(ring_x, ring_y),
            size=RenderSize(ring_width, ring_height),
            src="./src/assets/images/cursor_ring.png",
        )

    def draw(self, canvas: "ImageDraw"):
        # 그리기 직전에 위치 업데이트 (애니메이션 적용)
        if self.hidden == True:
            return
        self._update_children_positions()
        self._cursor_ring.draw(canvas)
        self._cursor_hat.draw(canvas)

    def _update_children_positions(self):
        cx, cy = self.coordinate.x, self.coordinate.y
        rh = self.size.height
        hh = self._cursor_hat.size.height

        self._cursor_ring.coordinate.x = cx
        self._cursor_ring.coordinate.y = cy

        current_time = time.time()

        bounce_ratio = abs(math.sin(current_time * math.pi))

        bounce_offset = -bounce_ratio * self._bounce_amplitude

        base_hat_y = cy - (rh // 2) - (hh // 2)

        self._cursor_hat.coordinate.x = cx
        self._cursor_hat.coordinate.y = int(base_hat_y + bounce_offset)
