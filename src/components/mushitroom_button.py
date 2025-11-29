import os
from typing import Callable
from PIL import Image, UnidentifiedImageError, ImageDraw

from src.classes.mushitroom_interface_object import noneFunction
from src.settings.mushitroom_enums import FontWeight
from src.classes.mushitroom_interface_object import MushitroomInterfaceObject
from src.utils.none_function import noneFunction
from src.utils.resource_loader import load_resized_image


class MushitroomButton(MushitroomInterfaceObject):
    button_href: str
    _image_cache: Image.Image | None

    def __init__(
        self,
        index: int,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        text: str | None = None,
        text_color: str = "black",
        font_size: int = 15,
        font_weight: FontWeight = FontWeight.REGULAR,
        id: str | None = None,
        on_action: Callable = noneFunction,
    ):
        super().__init__(
            index,
            x,
            y,
            width,
            height,
            color,
            text,
            text_color,
            font_size,
            font_weight,
            id,
            on_action,
        )
        self.button_href = "./src/assets/images/button.png"
        self._image_cache = load_resized_image(
            self.button_href, self.width, self.height
        )

    def draw(self, canvas: ImageDraw.ImageDraw):
        """
        캔버스에 이미지를 그립니다.
        주의: ImageDraw 객체는 paste를 지원하지 않으므로,
        ImageDraw가 참조하는 원본 Image 객체(_image)에 접근하여 그립니다.
        """
        half_width = self.width // 2
        half_height = self.height // 2

        # 중심 좌표를 기준으로 좌상단(Top-Left) 좌표 계산
        top_left_x = self.x - half_width
        top_left_y = self.y - half_height

        if self._image_cache:
            try:
                # ImageDraw 객체에서 내부 Image 객체를 가져옴 (Pillow 내부 속성 활용)
                target_image = getattr(canvas, "_image", None) or getattr(
                    canvas, "im", None
                )

                if isinstance(target_image, Image.Image):
                    # 투명도를 살리기 위해 mask=self._image_cache 사용
                    target_image.paste(
                        self._image_cache, (top_left_x, top_left_y), self._image_cache
                    )
                else:
                    # target_image를 찾을 수 없거나 타입이 안 맞으면 부모의 사각형 그리기(fallback)
                    super().draw(canvas)
            except Exception as e:
                # 그리기 실패 시 디버그용으로 사각형 그림
                print(f"Draw error: {e}")
                super().draw(canvas)
        else:
            # 이미지가 로드되지 않았으면 기본 사각형(placeholder) 그림
            super().draw(canvas)
