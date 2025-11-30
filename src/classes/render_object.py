from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw
    from src.classes.render_size import RenderSize
    from src.classes.render_coordinate import RenderCoordinate


class RenderObject:
    coordinate: "RenderCoordinate"
    size: "RenderSize"

    def __init__(
        self,
        coordinate: "RenderCoordinate",
        size: "RenderSize",
    ) -> None:
        self.coordinate = coordinate
        self.size = size
        pass

    def update(self):
        pass

    def draw(self, canvas: "ImageDraw"):
        pass
