from PIL import ImageDraw


class MushitroomObject:
    def __init__(self, x: int, y: int, size: int, color: str):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def update(self):
        pass  

    def draw(self, canvas: ImageDraw.ImageDraw):
        half = self.size // 2
        # 기본은 사각형으로 그리기
        canvas.rectangle(
            (self.x - half, self.y - half, self.x + half, self.y + half),
            fill=self.color,
            outline="white",
        )
