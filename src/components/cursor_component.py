import time
import math
from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_object import RenderObject
from classes.render_size import RenderSize
from components.render_image import RenderImage
from settings.mushitroom_config import ZOOM_IN

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class CursorComponent(RenderObject):
    _cursor_hat: RenderImage
    _cursor_ring: RenderImage

    # 애니메이션 설정
    _bounce_amplitude: int = 5

    def __init__(self, coordinate: RenderCoordinate, size: RenderSize) -> None:
        super().__init__(coordinate, size)

        # 사용자가 만족한 사이즈(더블 줌) 유지
        ring_width = size.width
        ring_height = size.height

        hat_width = ring_width
        hat_height = int(ring_height / 3)

        # 초기 좌표는 중요하지 않음 (update에서 덮어씌움)
        raw_x = coordinate.x
        raw_y = coordinate.y

        self._cursor_hat = RenderImage(
            coordinate=RenderCoordinate(raw_x, raw_y),
            size=RenderSize(hat_width, hat_height),
            src="./src/assets/images/cursor_hat.png",
        )

        self._cursor_ring = RenderImage(
            coordinate=RenderCoordinate(raw_x, raw_y),
            size=RenderSize(ring_width, ring_height),
            src="./src/assets/images/cursor_ring.png",
        )

    def draw(self, canvas: "ImageDraw"):
        if self.hidden == True:
            return
        self._update_children_positions()
        self._cursor_ring.draw(canvas)
        self._cursor_hat.draw(canvas)

    def _update_children_positions(self):
        cx, cy = self.coordinate.x, self.coordinate.y

        # [수정 핵심] 위치 계산 시 'self.size(1배 줌)'가 아니라
        # 'self._cursor_ring.size(2배 줌, 실제 보이는 크기)'를 기준으로 잡아야 함
        rh = self._cursor_ring.size.height
        hh = self._cursor_hat.size.height

        # 1. 링 배치
        self._cursor_ring.coordinate.x = cx
        self._cursor_ring.coordinate.y = cy

        # 2. 애니메이션 (줌인 적용)
        current_time = time.time()
        bounce_ratio = abs(math.sin(current_time * math.pi))
        bounce_offset = -bounce_ratio * self._bounce_amplitude * ZOOM_IN

        # 3. 모자 배치
        # 공식: (중앙Y) - (링 실제 높이 절반) - (모자 높이 절반)
        base_hat_y = cy - (rh // 2) - (hh // 2)

        self._cursor_hat.coordinate.x = cx
        self._cursor_hat.coordinate.y = int(base_hat_y + bounce_offset)
