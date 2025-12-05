import time
import math
from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_object import RenderObject
from classes.render_size import RenderSize
from components.render_image import RenderImage

# ZOOM_IN 변수가 이 파일 범위에서 사용 가능하도록 가정합니다.
# Assuming ZOOM_IN variable is accessible in this file scope.
from settings.mushitroom_config import ZOOM_IN

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class CursorComponent(RenderObject):
    _cursor_hat: RenderImage
    _cursor_ring: RenderImage
    _ring_hidden: bool

    # 애니메이션 설정
    _bounce_amplitude: int = 5

    def __init__(
        self,
        coordinate: RenderCoordinate,
        size: RenderSize,
        ring_hidden: bool = False,
    ) -> None:
        super().__init__(coordinate, size)
        self._ring_hidden = ring_hidden
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
        if self._ring_hidden == False:
            self._cursor_ring.draw(canvas)
        self._cursor_hat.draw(canvas)

    def _update_children_positions(self):
        cx, cy = self.coordinate.x, self.coordinate.y

        # 사이즈 가져오기
        rw, rh = self._cursor_ring.size.width, self._cursor_ring.size.height
        hw, hh = self._cursor_hat.size.width, self._cursor_hat.size.height

        # ---------------------------------------------------------
        # [수정 포인트] 위치 보정값 (음수 값의 절대값을 키울수록 모자가 위로 더 많이 올라가 Ring과 분리됩니다.)
        # 현재 -30으로 설정하여 Ring 침범을 방지하고 충분한 분리 공간을 확보했습니다.
        # 모자가 Ring을 침범한다면 이 값의 음수 절대값을 더 키우세요. (예: -35, -40)
        y_adjustment = -30
        # ---------------------------------------------------------

        # **[오류 수정] ZOOM_IN 변수의 타입 안정성 확보**
        zoom_factor = 1.0
        try:
            # ZOOM_IN을 float으로 안전하게 변환하여 사용합니다.
            # 변환에 실패하면 (예: None, 잘못된 문자열) 기본값 1.0을 사용합니다.
            zoom_factor = float(ZOOM_IN)
        except (ValueError, TypeError, NameError):
            # 혹시 모를 임포트 실패(NameError)나 잘못된 타입(ValueError, TypeError)에 대비
            print(
                f"Warning: ZOOM_IN value in config is invalid. Using default zoom factor of 1.0."
            )
            zoom_factor = 1.0
        # ---------------------------------------------------------

        # 1. 링 배치 (중앙 정렬)
        # 링의 Top-Left Y좌표
        ring_y = cy - (rh // 2)

        self._cursor_ring.coordinate.x = int(cx - (rw // 2))
        self._cursor_ring.coordinate.y = int(ring_y)

        # 2. 애니메이션 (위로 통통)
        current_time = time.time()
        bounce_ratio = abs(math.sin(current_time * math.pi * 2))

        # 수정된 65번째 줄: zoom_factor를 사용하여 안전하게 계산합니다.
        bounce_offset = -bounce_ratio * self._bounce_amplitude * zoom_factor

        # 3. 모자 배치
        self._cursor_hat.coordinate.x = int(cx - (hw // 2))

        # [계산 로직]
        # 링의 윗변(ring_y) - 모자 높이(hh) -> 딱 붙음
        # + y_adjustment (음수 값의 절대값을 키우면 위로 올라감)
        base_hat_y = ring_y - hh + y_adjustment

        self._cursor_hat.coordinate.y = int(base_hat_y + bounce_offset)
