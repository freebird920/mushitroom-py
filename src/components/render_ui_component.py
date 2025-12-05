from typing import TYPE_CHECKING, Callable, Optional
from src.classes.render_object import RenderObject

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class RenderUiComponent:
    is_selectable: bool
    render_object: RenderObject
    on_activate: Optional[Callable[[], None]]
    focused: bool

    def __init__(
        self,
        render_object: RenderObject,
        is_selectable: bool = False,
        on_activate: Optional[Callable[[], None]] = None,
        on_focus_callback: Optional[Callable] = None,
    ) -> None:
        self.focused = False
        self.render_object = render_object
        self.is_selectable = is_selectable
        self.on_activate = on_activate
        self.on_focus_callback = on_focus_callback
        pass

    def on_focus(self):
        """매니저가 호출할 메서드"""
        if self.on_focus_callback:
            self.on_focus_callback()

    def draw(self, canvas: "ImageDraw"):
        return self.render_object.draw(canvas)

    def run_callback(
        self,
        callback_function: Optional[Callable[[], None]],
    ):
        if callback_function is not None:
            return callback_function()

    def activate(self):
        if not self.is_selectable:
            return

        if self.on_activate:
            return self.on_activate()
