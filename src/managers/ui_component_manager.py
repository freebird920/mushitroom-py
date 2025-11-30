from typing import TYPE_CHECKING, List, Optional

from src.components.render_ui_component import RenderUiComponent

if TYPE_CHECKING:
    from PIL.ImageDraw import ImageDraw


class UiComponentManager:
    _ui_components: List[RenderUiComponent]
    _selected_index: int

    def __init__(self) -> None:
        self._ui_components = []
        self._selected_index = -1

    def goto_index(self, index: int):
        self._selected_index = index

    def add_component(self, component: RenderUiComponent) -> None:
        """UI 컴포넌트를 매니저에 등록합니다."""
        self._ui_components.append(component)

        # 만약 처음 추가된 '선택 가능한' 컴포넌트라면 바로 선택 상태로 둠
        if self._selected_index == -1 and component.is_selectable:
            self._selected_index = len(self._ui_components) - 1
            self._update_visual_feedback()  # (선택적) 선택된 녀석 색깔 바꾸기 등

    def draw(self, canvas: "ImageDraw") -> None:
        """등록된 모든 컴포넌트를 그립니다."""
        for component in self._ui_components:
            component.draw(canvas)

    def activate_current(self) -> None:
        """현재 선택된 컴포넌트의 activate 함수를 실행합니다."""
        if 0 <= self._selected_index < len(self._ui_components):
            target = self._ui_components[self._selected_index]
            target.activate()

    def select_next(self) -> None:
        """다음 선택 가능한 컴포넌트로 포커스를 이동합니다."""
        if not self._ui_components:
            return

        original_index = self._selected_index
        # 다음 인덱스부터 탐색 시작
        next_index = self._selected_index

        while True:
            # 인덱스 1 증가 (리스트 끝에 도달하면 0으로 돌아감: Modulo 연산)
            next_index = (next_index + 1) % len(self._ui_components)

            # 한 바퀴 다 돌아서 제자리로 왔으면 (선택 가능한 게 나 하나뿐이거나 없음) 중단
            if next_index == original_index:
                break

            # 선택 가능한 녀석을 찾으면 인덱스 업데이트하고 종료
            if self._ui_components[next_index].is_selectable:
                self._selected_index = next_index
                break

        self._update_visual_feedback()

    def select_prev(self) -> None:
        """이전 선택 가능한 컴포넌트로 포커스를 이동합니다."""
        if not self._ui_components:
            return

        original_index = self._selected_index
        prev_index = self._selected_index

        while True:
            prev_index = (prev_index - 1 + len(self._ui_components)) % len(
                self._ui_components
            )

            if prev_index == original_index:
                break

            if self._ui_components[prev_index].is_selectable:
                self._selected_index = prev_index
                break

        self._update_visual_feedback()
        pass

    def _update_visual_feedback(self) -> None:
        """현재 선택된 녀석과 선택되지 않은 녀석의 시각적 상태(색상 등)를 업데이트합니다."""
        for i, component in enumerate(self._ui_components):
            # [중요] 선택 불가능한 컴포넌트(라벨, 장식 등)는 건드리지 않고 건너뜀
            if not component.is_selectable:
                continue
        pass
