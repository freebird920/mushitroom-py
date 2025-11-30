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

    def __init__(self, coordinate: RenderCoordinate, size: RenderSize) -> None:
        super().__init__(coordinate, size)

        # 1. 사이즈 계산 (원본 비율 유지)
        # Ring: 320x120, Hat: 320x40 -> 높이 비율 3:1
        ring_width = size.width
        ring_height = size.height

        hat_width = ring_width
        hat_height = int(ring_height / 3)  # 높이는 1/3

        # 2. 좌표 계산
        # Ring은 중심 좌표(coordinate) 그대로 사용
        ring_x = coordinate.x
        ring_y = coordinate.y

        # Hat은 Ring 바로 위에 위치
        # Ring의 위쪽 끝 Y = (Ring 중심 Y) - (Ring 높이 / 2)
        # Hat의 중심 Y = (Ring 위쪽 끝 Y) - (Hat 높이 / 2)
        hat_x = coordinate.x
        hat_y = ring_y - (ring_height // 2) - (hat_height // 2)

        # 3. 이미지 컴포넌트 생성
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
        """
        그릴 때 현재 CursorComponent의 좌표(self.coordinate)에 맞춰
        자식 요소(Hat, Ring)의 위치를 업데이트하고 그립니다.
        """
        self._update_children_positions()

        # Ring을 먼저 그리고 Hat을 나중에 그려야 겹칠 경우 Hat이 위로 올라옴
        # (혹은 의도에 따라 순서 변경 가능)
        self._cursor_ring.draw(canvas)
        self._cursor_hat.draw(canvas)

    def _update_children_positions(self):
        """부모(CursorComponent)의 좌표가 변경되었을 경우 자식 위치 동기화"""
        # 현재 컴포넌트의 좌표와 사이즈 참조
        cx, cy = self.coordinate.x, self.coordinate.y
        rh = self.size.height
        hh = self._cursor_hat.size.height

        # Ring 위치 업데이트 (중심)
        self._cursor_ring.coordinate.x = cx
        self._cursor_ring.coordinate.y = cy

        # Hat 위치 업데이트 (Ring 바로 위)
        self._cursor_hat.coordinate.x = cx
        self._cursor_hat.coordinate.y = cy - (rh // 2) - (hh // 2)
