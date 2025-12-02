from typing import TYPE_CHECKING, List, Optional
from managers.sound_manager import AudioList, SoundManager
from components.render_ui_component import RenderUiComponent
from classes.render_object import RenderObject

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class UiComponentManager:
    sound_manager: SoundManager

    # [변경] 모든 렌더링 대상을 담는 리스트
    render_components: List[RenderUiComponent]
    # [추가] 선택 가능한 대상만 따로 관리하는 리스트 (네비게이션 용)
    selectable_components: List[RenderUiComponent]

    # 이 인덱스는 이제 render_components가 아니라 selectable_components 기준입니다.
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
        self.sound_manager = SoundManager()

        if self.cursor:
            self.cursor.hidden = True

    def clear_components(self, reset_index: bool = True) -> None:
        """
        모든 컴포넌트 리스트를 비웁니다.
        reset_index=False면 현재 커서가 가리키던 '순서'(예: 2번째 버튼)를 기억합니다.
        """
        self.render_components.clear()
        self.selectable_components.clear()

        if reset_index:
            self.selected_index = -1
        # reset_index가 False라도 리스트가 비워졌으므로 잠시 후 재설정이 필요합니다.
        # 하지만 인덱스 값 자체는 유지해서, 나중에 add_component 될 때 복구 시도합니다.

    def add_component(self, component: RenderUiComponent) -> None:
        """UI 컴포넌트를 등록합니다. 선택 가능한지 여부에 따라 자동으로 분류합니다."""
        # 1. 그리기 위해 전체 리스트에 등록
        self.render_components.append(component)

        # 2. 선택 가능하다면 네비게이션 리스트에도 등록
        if component.is_selectable:
            self.selectable_components.append(component)

            # 현재 추가된 선택 가능 항목의 인덱스 (0, 1, 2...)
            current_selectable_idx = len(self.selectable_components) - 1

            # [초기화 상황] 아무것도 선택 안 된 상태라면 첫 번째 항목 선택
            if self.selected_index == -1:
                self.selected_index = 0
                self._update_cursor_position()

            # [리스트 갱신 상황]
            # clear_components(reset_index=False)로 인해
            # "난 2번째 버튼이었어"라고 기억하고 있다면,
            # 지금 들어온 게 2번째 버튼일 때 커서 위치를 동기화해줍니다.
            elif self.selected_index == current_selectable_idx:
                self._update_cursor_position()

    def draw(self, canvas: "ImageDraw") -> None:
        # 그릴 때는 텍스트, 버튼 가리지 않고 다 그립니다.
        for component in self.render_components:
            component.draw(canvas)

        if self.cursor is not None and not self.cursor.hidden:
            self.cursor.draw(canvas)

    def _try_wake_up_cursor(self) -> bool:
        if self.cursor and self.cursor.hidden:
            self.cursor.hidden = False
            self._update_cursor_position()
            self.sound_manager.play_sound(AudioList.CLICK)
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

        # 선택 가능한 목록에서 현재 인덱스를 찾아서 실행
        if 0 <= self.selected_index < len(self.selectable_components):
            target = self.selectable_components[self.selected_index]
            target.activate()
            self._try_sleep_cursor()

    def select_next(self) -> None:
        if not self.selectable_components:
            return

        if self._try_wake_up_cursor():
            return

        # 단순한 인덱스 증가 (이미 선택 가능한 애들만 모여있으므로 루프 돌 필요 없음)
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

        # 단순한 인덱스 감소
        original_index = self.selected_index
        self.selected_index = (
            self.selected_index - 1 + len(self.selectable_components)
        ) % len(self.selectable_components)

        if original_index != self.selected_index:
            self._on_selection_changed()

    def _on_selection_changed(self) -> None:
        self.sound_manager.play_sound(AudioList.CLICK)
        self._update_cursor_position()

    def _update_cursor_position(self) -> None:
        """커서 위치를 선택된 컴포넌트 좌표로 이동시킵니다."""
        if not self.cursor:
            return

        # 선택 가능한 컴포넌트가 하나도 없으면 리턴
        if not self.selectable_components:
            return

        # 인덱스 범위 보정 (리스트가 줄어들었을 때)
        if self.selected_index >= len(self.selectable_components):
            self.selected_index = len(self.selectable_components) - 1

        if self.selected_index < 0:
            self.selected_index = 0

        # 좌표 동기화
        # 이제 selected_index는 selectable_components 리스트의 인덱스입니다.
        target_component = self.selectable_components[self.selected_index]
        target_obj = target_component.render_object

        if target_obj:
            self.cursor.coordinate.x = target_obj.coordinate.x
            self.cursor.coordinate.y = target_obj.coordinate.y
