from typing import TYPE_CHECKING, Callable, Optional
from src.classes.render_object import RenderObject

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class RenderUiComponent:
    is_selectable: bool
    render_object: RenderObject
    on_activate: Optional[Callable[[], None]]

    def __init__(
        self,
        render_object: RenderObject,
        is_selectable: bool = False,
        on_activate: Optional[Callable[[], None]] = None,
    ) -> None:
        self.render_object = render_object
        self.is_selectable = is_selectable
        self.on_activate = on_activate
        pass

    def draw(self, canvas: "ImageDraw"):
        return self.render_object.draw(canvas)

    def activate(self):
        if not self.is_selectable:
            return

        if self.on_activate:
            return self.on_activate()
