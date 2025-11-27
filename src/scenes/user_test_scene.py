from typing import TYPE_CHECKING, TypedDict, Unpack


from src.settings.mushitroom_enums import SceneType
from src.classes.scene_base import BaseScene


class UserSceneArgs(TypedDict):
    user: "User"


if TYPE_CHECKING:
    from src.managers.input_manager import InputState
    from src.managers.scene_manager import SceneManager
    from src.schemas.user_schema import User
    from src.services.sq_service import SqService


class UserTestScene(BaseScene):

    def __init__(self, manager: "SceneManager", db: "SqService"):
        super().__init__(manager, db)

    def on_enter(self, **kwargs: Unpack[UserSceneArgs]):  # type: ignore[override]
        super().on_enter()
        if kwargs["user"]:
            self.user = kwargs["user"]
            print(f"유저: {self.user.username}")

    def handle_input(self, input_state: "InputState"):
        super().handle_input(input_state)
        if "Escape" in input_state.just_pressed_keys:
            self.manager.switch_scene(SceneType.SELECT_USER)
