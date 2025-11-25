from PIL import ImageDraw
import uuid
from mushitroom_enums import ObjectType


class MushitroomObject:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        id: str | None = None,
        object_type: ObjectType = ObjectType.DEFAULT,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.object_type = object_type
        self.color = color
        if id is None:
            self.uuid = str(uuid.uuid4())
        else:
            # 밖에서 넣어줬으면(DB 로딩 등) -> 그걸 그대로 씀
            self.uuid = id

    def update(self):
        pass

    def draw(self, canvas: ImageDraw.ImageDraw):
        half_width = self.width // 2
        half_height = self.height // 2
        # 기본은 사각형으로 그리기
        canvas.rectangle(
            (
                self.x - half_width,
                self.y - half_height,
                self.x + half_width,
                self.y + half_height,
            ),
            fill=self.color,
            outline="white",
        )
