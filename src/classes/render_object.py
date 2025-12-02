from typing import TYPE_CHECKING


from classes.render_size import RenderSize
from settings.mushitroom_config import ZOOM_IN
from classes.render_coordinate import RenderCoordinate

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class RenderObject:
    coordinate: "RenderCoordinate"
    size: "RenderSize"
    hidden: bool

    def __init__(
        self, coordinate: RenderCoordinate, size: RenderSize, hidden: bool = False
    ) -> None:
        self.coordinate = RenderCoordinate(
            coordinate.x * ZOOM_IN, coordinate.y * ZOOM_IN
        )
        self.size = RenderSize(size.width * ZOOM_IN, size.height * ZOOM_IN)
        self.hidden = hidden
        pass

    def update(self):
        pass

    def draw(self, canvas: "ImageDraw"):
        if self.hidden == True:
            return
        pass
