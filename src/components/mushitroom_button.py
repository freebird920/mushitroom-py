from typing import Any, Callable

from src.classes.mushitroom_interface_object import noneFunction
from src.settings.mushitroom_enums import FontWeight
from src.classes.mushitroom_interface_object import MushitroomInterfaceObject
from src.utils.none_function import noneFunction


class MushitroomButton(MushitroomInterfaceObject):

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
