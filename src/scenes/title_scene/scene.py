import sys
from typing import Any, List, Tuple

from PIL.ImageDraw import ImageDraw
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from classes.scene_base import SceneBase
from components.cursor_component import CursorComponent
from components.mushroom_component import MushroomComponent
from components.render_ui_component import RenderUiComponent
from managers.audio_manager import AudioList
from managers.scene_manager import SceneManager  # 씬 전환을 위해 필요
from managers.ui_component_manager import UiComponentManager
from scenes.title_scene.ui_builder import TitleSceneUiBuilder
from settings.mushitroom_enums import InputActions, SceneType


class TitleScene(SceneBase):
    _ui_manager: UiComponentManager
    _ui_builder: TitleSceneUiBuilder
    _animated_components: List[Tuple[MushroomComponent, RenderUiComponent]]

    def __init__(self):
        super().__init__()
        # 커서 위치 및 크기 설정
        self._ui_manager = UiComponentManager(
            cursor=CursorComponent(
                coordinate=RenderCoordinate(0, 0),
                size=RenderSize(100, 30),
            )
        )
        self._ui_builder = TitleSceneUiBuilder()
        self._animated_components = []

    # [기능 1] 게임 시작 콜백
    def _on_start_game(self):
        print("Game Start!")
        # 다음 씬(예: 사용자 선택, 로비 등)으로 이동
        SceneManager().switch_scene(SceneType.SELECT_USER)

    # [기능 2] 게임 종료 콜백
    def _on_exit_game(self):
        print("Game Exit!")
        sys.exit(0)

    def handle_input(self):
        super().handle_input()
        if self._input_manager.state.is_just_pressed(InputActions.RIGHT):
            self._ui_manager.select_next()
        if self._input_manager.state.is_just_pressed(InputActions.LEFT):
            self._ui_manager.select_prev()

        # 엔터 키 입력 시 현재 선택된 버튼(RenderUiComponent)의 on_activate 실행
        if self._input_manager.state.is_just_pressed(InputActions.ENTER):
            self._ui_manager.activate_current()

    def on_enter(self, **kwargs: Any):
        super().on_enter(**kwargs)
        self._audio_manager.play_bgm(AudioList.BGM_00)

        # 컴포넌트 리스트 초기화
        self._ui_manager.clear_components()
        self._animated_components.clear()

        # 1. 타이틀 텍스트 추가
        self._ui_manager.add_component(self._ui_builder._title_text_component)

        # 2. 버튼 생성 및 추가 (여기서 콜백 함수 연결)
        buttons = self._ui_builder.build_buttons(
            on_start=self._on_start_game, on_exit=self._on_exit_game
        )
        for btn in buttons:
            self._ui_manager.add_component(btn)

        # 3. 버섯 추가 및 애니메이션 등록
        for busot in self._ui_builder._busots:
            current_img_comp = busot.rotate(True)
            ui_comp = RenderUiComponent(
                render_object=current_img_comp, is_selectable=False, on_activate=None
            )
            self._ui_manager.add_component(ui_comp)
            self._animated_components.append((busot, ui_comp))

    def update(self):
        super().update()
        # 애니메이션 처리
        for busot, ui_comp in self._animated_components:
            next_image = busot.rotate(True)
            ui_comp.render_object = next_image

    def draw(self, draw_tool: ImageDraw):
        self._ui_manager.draw(draw_tool)
        super().draw(draw_tool)
