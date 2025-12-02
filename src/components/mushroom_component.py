from typing import List
from classes.mushroom_class import MushroomType
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.mushroom_image_component import MushroomImageComponent


class MushroomComponent:
    mushroom_type: MushroomType
    mushroom_direction: int
    mushroom_images: List[MushroomImageComponent]
    coordinate: RenderCoordinate
    size: RenderSize

    def __init__(
        self,
        mushroom_type: MushroomType,
        coordinate: RenderCoordinate,
        size: RenderSize,
    ) -> None:
        self.mushroom_direction = 1
        self.mushroom_type = mushroom_type
        self.size = size
        self.coordinate = coordinate
        self.mushroom_images = []
        for i in range(1, 6, 1):
            self.mushroom_images.append(
                MushroomImageComponent(
                    mushroom_type=self.mushroom_type,
                    direction=i,
                    coordinate=self.coordinate,
                    size=self.size,
                )
            )
        pass
