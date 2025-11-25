import PIL.Image
import PIL.ImageDraw
from PIL import ImageTk
import platform
import time
from mushitroom_interface_object import MushitroomInterfaceObject
from mushitroom_interface_object import MushitroomInterfaceGroup


# ============
# 설정파일 불러오기
# ============
import mushitroom_config

WIDTH: int = mushitroom_config.DISPLAY_WIDTH
HEIGHT: int = mushitroom_config.DISPLAY_HEIGHT
BG_COLOR = mushitroom_config.BG_COLOR
FPS = int(1000 / mushitroom_config.FPS)

# ============
# Windows 전용 설정
# ============
"""python
if root is not None:
    windows일 때 실행할 코드
"""
import tkinter as tk

root: tk.Tk | None = None
is_windows = platform.system() == "Windows"
if is_windows:
    root = tk.Tk()
    root.title("MUSHITROOM")
    label = tk.Label(root)
    label.pack()


# ============
# objects
# ============
import mushitroom_object

objects: list[mushitroom_object.MushitroomObject] = []

shit_1 = mushitroom_object.MushitroomObject(
    x=10, y=10, width=20, height=20, color="black"
)

button_01 = mushitroom_object.MushitroomObject(
    x=100, y=250, width=100, height=50, color="#F0F0F0"
)

button_02 = mushitroom_object.MushitroomObject(
    x=200, y=250, width=100, height=50, color="#FF0000"
)
ui_manager = MushitroomInterfaceGroup()
# 2. 버튼 생성 (이제 index를 일일이 안 넣어줘도 됨, 넣는 순서대로니까)
from mushitroom_enums import FontWeight

btn_start = MushitroomInterfaceObject(
    index=0,
    x=100,
    y=100,
    width=120,
    height=40,
    color="white",
    text="START",
    font_weight=FontWeight.HEAVY,
)
btn_exit = MushitroomInterfaceObject(
    index=1,
    x=100,
    y=160,
    width=120,
    height=40,
    color="white",
    text="EXIT",
    font_weight=FontWeight.HEAVY,
)

# 3. 그룹에 추가 (이러면 알아서 0번인 START가 선택됨)
ui_manager.add_element(btn_start)
ui_manager.add_element(btn_exit)


objects.append(button_01)
objects.append(button_02)
objects.append(shit_1)

# ====
# 키보드 이벤트 (Windows에서 Test 하기 위함)
# ====

pressed_keys: set[str] = set()
just_pressed_keys: set[str] = set()


def on_key_press(event):
    if event.keysym not in pressed_keys:
        just_pressed_keys.add(event.keysym)
    pressed_keys.add(event.keysym)


def on_key_release(event):
    # 키보드를 떼면 set에서 제거
    if event.keysym in pressed_keys:
        pressed_keys.remove(event.keysym)
    just_pressed_keys.clear()


def keyboard_event():
    # =====
    # 딸깎뀪용
    # =====
    if "Up" in pressed_keys or "w" in pressed_keys:
        shit_1.y = shit_1.y - 1
        print("위")
    if "Down" in pressed_keys or "s" in pressed_keys:
        print("아래")

        shit_1.y = shit_1.y + 1
    if "Left" in pressed_keys or "a" in pressed_keys:
        shit_1.x = shit_1.x - 1

        print("좌")
    if "Right" in pressed_keys or "d" in pressed_keys:
        shit_1.x = shit_1.x + 1
        print("우")

    # =====
    # 한 번 딸깍 용
    # =====
    if "bracketleft" in just_pressed_keys:
        ui_manager.select_prev()
    if "bracketright" in just_pressed_keys:
        ui_manager.select_next()
        print("망할게 ㅋㅋ")
    just_pressed_keys.clear()


# keyboard event 바인드
if root is not None:
    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)


# =====
# 화면 그리기
# =====
def draw_frame() -> PIL.Image.Image:
    # canvas
    canvas = PIL.Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    # draw_tool 선언
    draw_tool = PIL.ImageDraw.Draw(canvas)
    ui_manager.draw(draw_tool)
    for obj in objects:
        obj.draw(draw_tool)
    return canvas


def main_logic():
    # 키보드 이벤트 처리하고
    keyboard_event()
    # 프레임 그리고 리턴
    return draw_frame()


def main_loop():
    if root is not None:
        pil_image = main_logic()
        tk_image = ImageTk.PhotoImage(pil_image)
        label.config(image=tk_image)
        label.image = tk_image  # type: ignore
        root.after(FPS, main_loop)
    else:
        while True:
            pil_image = main_logic()
            # 나중에 여기에 device.display(pil_image) 추가
            time.sleep(FPS / 1000)


def main():
    main_loop()
    if root is not None:
        root.mainloop()


if __name__ == "__main__":
    main()
