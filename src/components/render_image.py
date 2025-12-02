# import pillow
from PIL.ImageDraw import ImageDraw
from PIL import Image

# import utils
from settings.mushitroom_config import ZOOM_IN
from utils.resource_loader import load_resized_image
# import classes
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.render_object import RenderObject


class RenderImage(RenderObject):
    color: str
    _image_cache: Image.Image | None

    def __init__(
        self, coordinate: RenderCoordinate, size: RenderSize, src: str
    ) -> None:
        super().__init__(coordinate, size)
        # 1. 이미지 로드
        # img_path = os.path.join(current_dir, "../", "assets", "images", "button.png")
        self._image_cache = load_resized_image(
            path=src,
            width=self.size.width,
            height=self.size.height,
        )

    def update(self):
        return super().update()

    def draw(self, canvas: ImageDraw):
        half_width = self.size.width // 2
        half_height = self.size.height // 2
        top_left_x = (self.coordinate.x - half_width) * ZOOM_IN
        top_left_y = self.coordinate.y - half_height * ZOOM_IN

        image_drawn = False
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
