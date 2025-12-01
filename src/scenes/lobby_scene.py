from collections import UserDict
from classes.scene_base import BaseScene
from managers.sound_manager import SoundManager
from managers.sq_manager import SqService
from managers.ui_component_manager import UiComponentManager
from schemas.user_schema import GameState, User


class LobbyScene(BaseScene):
    ui_component_manager: UiComponentManager
    sound_manager: SoundManager
    game_state: GameState | None
    _user_id: str

    def __init__(self, user_id: str):
        super().__init__()
        self.db = SqService()
        self.sound_manager
        self._user_id = user_id

    def on_enter(self):
        super().on_enter()
        game_state = self.db.get_full_game_state(self._user_id)
        if game_state is None:
            self.db.save_game_state(
                user_id=self._user_id,
                money=20,
                days=0,
            )
            game_state = self.db.get_full_game_state(self._user_id)

    def on_exit(self):
        return super().on_exit()
