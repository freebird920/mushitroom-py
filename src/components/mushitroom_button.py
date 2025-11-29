import os
from typing import Callable
from PIL import Image, ImageDraw, ImageFont

# 기존 import 유지
from src.classes.mushitroom_interface_object import MushitroomInterfaceObject
from src.settings.mushitroom_enums import FontWeight
from src.utils.none_function import noneFunction
from src.utils.resource_loader import load_custom_font, load_resized_image


class MushitroomButton(MushitroomInterfaceObject):
    button_href: str
    _image_cache: Image.Image | None
    _font: ImageFont.ImageFont | ImageFont.FreeTypeFont

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

        # [수정] 실행 위치에 상관없이 안전하게 경로 계산
        current_dir = os.path.dirname(__file__)

        # 1. 이미지 로드
        img_path = os.path.join(current_dir, "../", "assets", "images", "button.png")
        self._image_cache = load_resized_image(
            path=img_path, width=self.width, height=self.height
        )

        # 2. 폰트 로드 (나눔스퀘어네오 하드코딩 된 경로 안전하게 수정)
        font_path = os.path.join(
            current_dir, "../", "assets", "fonts", "NanumSquareNeo-bRg.ttf"
        )
        self._font = load_custom_font(path=font_path, size=font_size)

    def draw(self, canvas: ImageDraw.ImageDraw):
        """
        이미지를 먼저 그리고, 그 중앙에 텍스트를 올립니다.
        """
        # 1. 이미지 그리기 (배경)
        half_width = self.width // 2
        half_height = self.height // 2
        top_left_x = self.x - half_width
        top_left_y = self.y - half_height

        image_drawn = False  # 이미지를 성공적으로 그렸는지 확인용

        if self._image_cache:
            try:
                target_image = getattr(canvas, "_image", None) or getattr(
                    canvas, "im", None
                )

                if isinstance(target_image, Image.Image):
                    target_image.paste(
                        self._image_cache, (top_left_x, top_left_y), self._image_cache
                    )
                    image_drawn = True
                else:
                    super().draw(canvas)  # fallback
            except Exception as e:
                print(f"Draw error: {e}")
                super().draw(canvas)  # fallback

        if not image_drawn and not self._image_cache:
            super().draw(canvas)

        # 2. 텍스트 그리기 (이미지 위에 덮어쓰기)
        if self.text:
            # 선택 여부에 따른 색상 변경 (부모 클래스의 is_selected 활용)
            current_color = (
                "red" if getattr(self, "is_selected", False) else self.text_color
            )

            canvas.text(
                (self.x, self.y),  # 버튼의 중심 좌표
                self.text,  # 텍스트 내용
                font=self._font,  # 로드된 폰트
                fill=current_color,  # 글자 색상
                anchor="mm",  # [핵심] Middle-Middle: 텍스트의 정중앙을 좌표에 맞춤
                align="center",  # 여러 줄일 경우 가운데 정렬
            )
