from PIL import ImageDraw
from typing import TYPE_CHECKING, Optional


# 기존 MushitroomObject를 import (타입 힌팅용)
# from src.objects.mushitroom_object import MushitroomObject
if TYPE_CHECKING:
    from src.classes.mushitroom_object import MushitroomObject


class UiCursor:
    def __init__(self, padding: int = 4, color: str = "red", line_width: int = 3):
        self.target: Optional["MushitroomObject"] = None
        self.padding = padding
        self.color = color
        self.line_width = line_width

    def set_target(self, obj: "MushitroomObject"):
        """커서가 가리킬 목표물을 설정합니다."""
        self.target = obj

    def update(self):
        # 나중에 여기에 애니메이션(부드러운 이동) 로직을 넣을 수 있습니다.
        pass

    def draw(self, canvas: ImageDraw.ImageDraw):
        """타겟 오브젝트 주변에 테두리를 그립니다."""
        if self.target is None:
            return

        # 타겟의 좌표와 크기를 가져옵니다.
        # MushitroomObject는 중심점(x, y) 기준이므로 계산이 필요합니다.
        t = self.target
        half_w = t.width // 2
        half_h = t.height // 2

        # 타겟보다 padding만큼 더 크게 영역을 잡습니다.
        left = t.x - half_w - self.padding
        top = t.y - half_h - self.padding
        right = t.x + half_w + self.padding
        bottom = t.y + half_h + self.padding

        # 테두리 그리기 (fill=None으로 하면 내부가 투명한 사각형이 됩니다)
        canvas.rectangle(
            (left, top, right, bottom), outline=self.color, width=self.line_width
        )
