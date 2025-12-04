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

        # 사이즈 가져오기
        rw, rh = self._cursor_ring.size.width, self._cursor_ring.size.height
        hw, hh = self._cursor_hat.size.width, self._cursor_hat.size.height

            # ---------------------------------------------------------
            # [수정 포인트] 위치 보정값
            # 침투하고 있다면 값을 '음수(-)'로 바꿔서 위로 올리세요.
            # 예: -10, -15 등으로 숫자를 바꿔가며 딱 맞는 위치를 찾으세요.
            y_adjustment = -23
            # ---------------------------------------------------------

        # 1. 링 배치 (중앙 정렬)
        # 링의 Top-Left Y좌표
        ring_y = cy - (rh // 2)

        self._cursor_ring.coordinate.x = int(cx - (rw // 2))
        self._cursor_ring.coordinate.y = int(ring_y)

        # 2. 애니메이션 (위로 통통)
        current_time = time.time()
        bounce_ratio = abs(math.sin(current_time * math.pi * 2))
        bounce_offset = -bounce_ratio * self._bounce_amplitude * ZOOM_IN

        # 3. 모자 배치
        self._cursor_hat.coordinate.x = int(cx - (hw // 2))

        # [계산 로직]
        # 링의 윗변(ring_y) - 모자 높이(hh) -> 딱 붙음
        # + y_adjustment (음수니까 위로 올라감)
        base_hat_y = ring_y - hh + y_adjustment

        self._cursor_hat.coordinate.y = int(base_hat_y + bounce_offset)
