from typing import TYPE_CHECKING, List, Optional
from managers.audio_manager import AudioList, AudioManager
from components.render_ui_component import RenderUiComponent
from classes.render_object import RenderObject

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class UiComponentManager:
    sound_manager: AudioManager
    render_components: List[RenderUiComponent]
    selectable_components: List[RenderUiComponent]
    selected_index: int
    cursor: Optional[RenderObject]

    def __init__(
        self,
        cursor: Optional[RenderObject] = None,
    ) -> None:
        self.render_components = []
        self.selectable_components = []
        self.selected_index = -1
        self.cursor = cursor
        self.sound_manager = AudioManager()

        if self.cursor:
            self.cursor.hidden = True

    def clear_components(self, reset_index: bool = True) -> None:
        self.render_components.clear()
        self.selectable_components.clear()
        print("ui_manager cleared")
        if reset_index:
            self.selected_index = -1

    def add_component(self, component: RenderUiComponent) -> None:
        self.render_components.append(component)

        if component.is_selectable:
            self.selectable_components.append(component)
            current_selectable_idx = len(self.selectable_components) - 1

            if self.selected_index == -1:
                self.selected_index = 0
                self._update_cursor_position()
            elif self.selected_index == current_selectable_idx:
                self._update_cursor_position()

    def draw(self, canvas: "ImageDraw") -> None:
        for component in self.render_components:
            component.draw(canvas)

        if self.cursor is not None and not self.cursor.hidden:
            self.cursor.draw(canvas)

    def _try_wake_up_cursor(self) -> bool:
        if self.cursor and self.cursor.hidden:
            self.cursor.hidden = False
            self._update_cursor_position()
            self.sound_manager.play_sfx(AudioList.CLICK)
            return True
        return False

    def _try_sleep_cursor(self) -> bool:
        if self.cursor and not self.cursor.hidden:
            self.cursor.hidden = True
            return True
        return False

    def activate_current(self) -> None:
        if self._try_wake_up_cursor():
            return

        if 0 <= self.selected_index < len(self.selectable_components):
            target = self.selectable_components[self.selected_index]
            target.activate()
            self._try_sleep_cursor()

    def select_next(self) -> None:
        if not self.selectable_components:
            return

        if self._try_wake_up_cursor():
            return

        original_index = self.selected_index
        self.selected_index = (self.selected_index + 1) % len(
            self.selectable_components
        )

        if original_index != self.selected_index:
            self._on_selection_changed()

    def select_prev(self) -> None:
        if not self.selectable_components:
            return

        if self._try_wake_up_cursor():
            return

        original_index = self.selected_index
        self.selected_index = (
            self.selected_index - 1 + len(self.selectable_components)
        ) % len(self.selectable_components)

        if original_index != self.selected_index:
            self._on_selection_changed()

    def _on_selection_changed(self) -> None:
        self.sound_manager.play_sfx(AudioList.CLICK)
        self._update_cursor_position()

    def _update_cursor_position(self) -> None:
        """커서 위치를 선택된 컴포넌트의 '중앙' 좌표로 이동시킵니다."""
        if not self.cursor or not self.selectable_components:
            return

        if self.selected_index >= len(self.selectable_components):
            self.selected_index = len(self.selectable_components) - 1

        if self.selected_index < 0:
            self.selected_index = 0

        target_component = self.selectable_components[self.selected_index]
        target_obj = target_component.render_object

        if target_obj:
            # 1. 기본 좌표 가져오기
            center_x = target_obj.coordinate.x
            center_y = target_obj.coordinate.y

            center_x += target_obj.size.width // 2
            center_y += target_obj.size.height // 2

            # 3. 커서에게 최종 중앙 좌표 전달
            self.cursor.coordinate.x = center_x
            self.cursor.coordinate.y = center_y
