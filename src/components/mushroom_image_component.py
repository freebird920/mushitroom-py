from PIL.ImageDraw import ImageDraw
from classes.mushroom_class import MushroomType
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.render_image import RenderImage


class MushroomImageComponent(RenderImage):
    def __init__(
        self,
        coordinate: RenderCoordinate,
        size: RenderSize,
        mushroom_type: MushroomType,
        direction: int = 1,
    ) -> None:
        mushroom_image_src: str = (
            "./src/assets/images/" + mushroom_type.image_name + str(direction) + ".png"
        )
        super().__init__(coordinate, size, mushroom_image_src)

    def draw(self, canvas: ImageDraw):

        super().draw(canvas)
