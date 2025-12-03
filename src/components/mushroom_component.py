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
        # 1~5 방향의 이미지를 미리 생성 (인덱스 0~4에 저장됨)
        for i in range(1, 6, 1):
            self.mushroom_images.append(
                MushroomImageComponent(
                    mushroom_type=self.mushroom_type,
                    direction=i,
                    coordinate=self.coordinate,
                    size=self.size,
                )
            )

    def rotate(self, clock_wise: bool) -> MushroomImageComponent:
        """
        버섯을 회전시키고, 회전된 결과에 맞는 MushroomImageComponent를 반환합니다.
        """
        if clock_wise:
            self.mushroom_direction += 1
            if self.mushroom_direction > 5:
                self.mushroom_direction = 1
        else:
            self.mushroom_direction -= 1
            if self.mushroom_direction < 1:
                self.mushroom_direction = 5

        # 방향(1~5)을 리스트 인덱스(0~4)로 변환하여 해당 이미지 컴포넌트 반환
        return self.mushroom_images[self.mushroom_direction - 1]
