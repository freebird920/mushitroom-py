import os
from PIL import Image, ImageDraw, UnidentifiedImageError
from src.classes.mushitroom_object import MushitroomObject
from src.settings.mushitroom_enums import ObjectType


class PngObject(MushitroomObject):
    href: str
    _image_cache: Image.Image | None  # 로드된 이미지를 저장할 변수
    velocity_y: float

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        object_id: str | None = None,
        object_type: ObjectType = ObjectType.DEFAULT,
        href: str = "",
        velocity_y: float = 0.00,
    ):
        super().__init__(x, y, width, height, color, object_id, object_type)
        self.href = href
        self._image_cache = None
        self._load_and_resize_image()
        self.velocity_y = velocity_y

    def _load_and_resize_image(self):
        """이미지를 로드하고 크기를 조절하여 캐시에 저장합니다."""
        if not self.href or not os.path.exists(self.href):
            print(f"Warning: Image path not found: {self.href}")
            return

        try:
            # 이미지 열기 및 RGBA 변환 (투명도 지원)
            with Image.open(self.href) as img:
                img = img.convert("RGBA")
                # 객체의 width, height에 맞춰 리사이징
                # Pi Zero 성능을 위해 리사이징 품질은 기본값(NEAREST) 또는 BILINEAR 권장
                self._image_cache = img.resize((self.width, self.height))
        except UnidentifiedImageError:
            print(f"Error: Cannot identify image file: {self.href}")
        except Exception as e:
            print(f"Error loading image {self.href}: {e}")

    def update(self):
        # 필요하다면 여기에 애니메이션 로직 추가
        pass

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
