from typing import Any
from classes.scene_base import BaseScene
from managers.audio_manager import AudioList
from settings.mushitroom_enums import InputActions, SceneType


class FeedScene(BaseScene):
    def __init__(self):
        super().__init__()

    def on_enter(self, **kwargs: Any):
        super().on_enter(**kwargs)
        self._audio_manager.play_bgm(AudioList.BGM_00)
        self.user_id = kwargs.get("user_id")

    def handle_input(self):
        super().handle_input()
        if self._input_manager.state.is_just_pressed(action=InputActions.ESCAPE):
            self._scene_manager.switch_scene(SceneType.LOBBY_SCENE)
