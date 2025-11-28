from typing import TYPE_CHECKING, TypedDict, Unpack

from PIL.ImageDraw import ImageDraw
from src.classes.mushitroom_interface_object import (
    MushitroomInterfaceGroup,
    MushitroomInterfaceObject,
)
from src.settings.mushitroom_enums import SceneType


from src.classes.scene_base import BaseScene

if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from src.managers.scene_manager import SceneManager
    from src.services.sq_service import SqService
    from src.schemas.user_schema import User


class PhisingTestSceneArgs(TypedDict):
    user: "User"


class PhishingTestScene(BaseScene):
    user: "User | None"
    current_number: int
    correct_range: int
    min: int
    max: int
    ui_group: MushitroomInterfaceGroup

    def __init__(
        self,
        manager: "SceneManager",
        db: "SqService",
    ):
        super().__init__(manager, db)
        self.ui_group = MushitroomInterfaceGroup()
        self.user_name_ui = MushitroomInterfaceObject(
            index=0,
            x=30,
            y=10,
            width=110,
            height=10,
            color="white",
            text="",
            text_color="white",
        )

    def handle_input(self, input_state: "InputState"):
        super().handle_input(input_state)
        if "Escape" in input_state.just_pressed_keys:
            self.manager.switch_scene(scene_type=SceneType.SELECT_USER)

    def on_enter(self, **kwargs: Unpack[PhisingTestSceneArgs]):  # type: ignore[override]
        super().on_enter()
        self.user = kwargs.get("user")
        if self.user is None:
            print("user없음 에러용")
            exit()
        self.user_name_ui.text = self.user.username

    def draw(self, draw_tool: ImageDraw):
        super().draw(draw_tool)
        self.ui_group.draw(draw_tool)
