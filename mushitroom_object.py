from PIL import ImageDraw


class MushitroomObject:
    def __init__(self, x: int, y: int, width: int, height: int, color: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.color = color

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
