from typing import TYPE_CHECKING
from classes.render_coordinate import RenderCoordinate
from classes.render_size import RenderSize
from components.cursor_component import CursorComponent
from components.mushroom_component import MushroomComponent
from components.render_button import RenderButton
from components.render_text import RenderText
from components.render_ui_component import RenderUiComponent
from managers.timer_manager import TimerManager
from scenes.mushroom_select_scene import logic
from settings.mushitroom_config import CENTER_X, CENTER_Y
from settings.mushitroom_enums import FontStyle

if TYPE_CHECKING:
    from scenes.mushroom_select_scene.scene import SelectMushroomScene


def build_mushrooms(scene: "SelectMushroomScene") -> None:
    if scene._game_state is None or scene._game_state.mushitrooms is None:
        print("NO MUSHIT ROOMS")
        return
    scene._mushroom_ui_manager.cursor = CursorComponent(
        coordinate=RenderCoordinate(0, 0),
        size=RenderSize(50, 50),
        ring_hidden=True,
    )
    scene._mushroom_ui_manager.cursor.hidden = True
    scene._mushroom_ui_manager.disable(True)
    for index, mushit_id in enumerate(scene._game_state.mushitrooms):
        print(index)
        mushit_info = scene.db.get_mushitroom(mushit_id)
        if mushit_info is None or mushit_info.type is None:
            return print("NO MUSHIT INFO")
        mushit_position_x = CENTER_X
        if index == 0:
            mushit_position_x = CENTER_X
        elif index == 1:
            mushit_position_x = CENTER_X - (CENTER_X // 2)
        elif index == 2:
            mushit_position_x = CENTER_X + (CENTER_X // 2)
        mushit_position = RenderCoordinate(
            mushit_position_x,
            CENTER_Y - (CENTER_Y // 3),
        )
        # 1. 버섯 컴포넌트 생성
        mushit_img = MushroomComponent(
            mushroom_type=mushit_info.type,
            coordinate=mushit_position,
            size=RenderSize(50, 50),
        )

        # 2. UI 컴포넌트 생성
        mushit_ui_comp = RenderUiComponent(
            render_object=mushit_img.mushroom_images[0],
            is_selectable=True,
            on_activate=None,
        )

        # ... 텍스트 컴포넌트 생성 및 매니저 등록 (기존 코드) ...
        mushit_name_text = RenderText(
            text=mushit_info.name,
            coordinate=RenderCoordinate(mushit_position.x, mushit_position.y + 50),
            font_size=10,
            font_style=FontStyle.COOKIE_BOLD,
        )
        mushit_name_comp = RenderUiComponent(
            render_object=mushit_name_text,
        )

        def jump_mushit_room(u_comp: RenderUiComponent):
            u_comp.render_object.coordinate = RenderCoordinate(
                u_comp.render_object.coordinate.x,
                u_comp.render_object.coordinate.y - 30,
            )

        def create_focus_animator(m_comp: MushroomComponent, u_comp: RenderUiComponent):
            # 마지막으로 회전한 시간을 기억하는 변수
            last_rotate_time = 0.0

            def on_focus_logic():
                """
                on_focus_logic의 Docstring

                ## nonlocal
                파이썬에서는 함수 안에서 변수 = 값 이렇게 할당을 하면, **"아, 이건 이 함수 안에서만 쓰는 새 변수구나"**라고 판단해 버립니다.

                * nonlocal이 없으면: on_focus_logic 안에서 last_rotate_time = current_time을 하는 순간, 바깥의 변수를 갱신하는 게 아니라 새로운 지역 변수를 만들어버립니다. (회전이 안 됨)

                * nonlocal이 있으면: "새로 만드는 거 아니고, 바로 위 함수(공장장)가 가지고 있던 그 변수 고칠 거야!" 라고 알려주는 것입니다.
                """
                nonlocal last_rotate_time
                # TimerManager에게 "게임 시작하고 얼마나 지났어?"라고 물어봄 (안전함)
                current_time = TimerManager().get_elapsed_time()

                if current_time - last_rotate_time > 0.1:
                    u_comp.render_object = m_comp.rotate(True)
                    last_rotate_time = current_time

            return on_focus_logic

        mushit_ui_comp.on_focus_callback = create_focus_animator(
            mushit_img, mushit_ui_comp
        )
        mushit_ui_comp.on_activate = lambda u=mushit_ui_comp: jump_mushit_room(u)
        # ---------------------------------------------------------
        scene._mushroom_ui_manager.add_component(mushit_name_comp)
        scene._mushroom_ui_manager.add_component(mushit_ui_comp)

    return scene.update()


def build_mushroom_select_scene_ui(scene: "SelectMushroomScene"):
    _ui_manager = scene._ui_manager
    _ui_manager.cursor = CursorComponent(
        coordinate=RenderCoordinate(0, 0),
        size=RenderSize(320 // 3, 100 // 3),
    )

    # buttons
    adopt_button = RenderButton(
        coordinate=RenderCoordinate(CENTER_X, CENTER_Y + (CENTER_Y // 2)),
        size=RenderSize(320 // 3, 100 // 3),
        font_size=14,
        font_style=FontStyle.COOKIE_BOLD,
        text="ADOPT",
    )
    adopt_button_component = RenderUiComponent(
        render_object=adopt_button,
        on_activate=lambda: logic.adopt_mushroom(scene=scene),
        is_selectable=True,
    )
    _ui_manager.add_component(adopt_button_component)
