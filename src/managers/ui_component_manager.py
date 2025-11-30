from typing import TYPE_CHECKING, List, Optional
from src.components.render_ui_component import RenderUiComponent
from src.classes.render_object import RenderObject

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class UiComponentManager:
    ui_components: List[RenderUiComponent]
    selected_index: int
    cursor: Optional[RenderObject]
    # cursor_offset_x 변수 제거함

    def __init__(
        self,
        cursor: Optional[RenderObject] = None,
        # offset 인자 제거함
    ) -> None:
        self.ui_components = []
        self.selected_index = -1
        self.cursor = cursor

    def goto_index(self, index: int):
        self.selected_index = index
        self._update_visual_feedback()
        self._update_cursor_position()

    def add_component(self, component: RenderUiComponent) -> None:
        """UI 컴포넌트를 매니저에 등록합니다."""
        self.ui_components.append(component)

        if self.selected_index == -1 and component.is_selectable:
            self.selected_index = len(self.ui_components) - 1
            self._update_visual_feedback()
            self._update_cursor_position()

    def draw(self, canvas: "ImageDraw") -> None:
        """등록된 모든 컴포넌트를 그립니다."""
        for component in self.ui_components:
            component.draw(canvas)

        # 커서를 마지막에 그려야 버튼 위에 덮어씌워짐 (테두리 등일 경우)
        if self.cursor is not None:
            self.cursor.draw(canvas)

    def activate_current(self) -> None:
        if 0 <= self.selected_index < len(self.ui_components):
            target = self.ui_components[self.selected_index]
            target.activate()

    def select_next(self) -> None:
        if not self.ui_components:
            return

        original_index = self.selected_index
        next_index = self.selected_index

        while True:
            next_index = (next_index + 1) % len(self.ui_components)
            if next_index == original_index:
                break
            if self.ui_components[next_index].is_selectable:
                self.selected_index = next_index
                break

        self._update_visual_feedback()
        self._update_cursor_position()

    def select_prev(self) -> None:
        if not self.ui_components:
            return

        original_index = self.selected_index
        prev_index = self.selected_index

        while True:
            prev_index = (prev_index - 1 + len(self.ui_components)) % len(
                self.ui_components
            )
            if prev_index == original_index:
                break
            if self.ui_components[prev_index].is_selectable:
                self.selected_index = prev_index
                break

        self._update_visual_feedback()
        self._update_cursor_position()

    def _update_visual_feedback(self) -> None:
        for i, component in enumerate(self.ui_components):
            if not component.is_selectable:
                continue
        pass

    def _update_cursor_position(self) -> None:
        """현재 선택된 컴포넌트 위치로 커서를 정확히 이동시킵니다."""
        if not self.cursor or self.selected_index == -1:
            return

        target_component = self.ui_components[self.selected_index]
        target_obj = target_component.render_object

        if target_obj:
            # [수정됨] 오프셋 계산 없이 타겟 좌표와 100% 일치시킴
            # RenderObject의 coordinate는 보통 객체의 중심(Center) 좌표입니다.
            # 따라서 커서의 중심이 버튼의 중심과 정확히 겹치게 됩니다.
            self.cursor.coordinate.x = target_obj.coordinate.x
            self.cursor.coordinate.y = target_obj.coordinate.y
