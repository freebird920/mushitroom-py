from typing import Any
from classes.scene_base import SceneBase
from managers.audio_manager import AudioList


class FeedScene(SceneBase):
    def __init__(self):
        super().__init__()

    def on_enter(self, **kwargs: Any):
        super().on_enter(**kwargs)
        self._audio_manager.play_bgm(AudioList.BGM_00)
