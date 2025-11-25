import mushitroom_config as cfg
import PIL.Image
import PIL.ImageDraw
from PIL import ImageTk
import platform
import time
import mushitroom_object


# ============
# 설정파일 불러오기
# ============
WIDTH: int = cfg.DISPLAY_WIDTH
HEIGHT: int = cfg.DISPLAY_HEIGHT
BG_COLOR = cfg.BG_COLOR
FPS = int(1000 / cfg.FPS)

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
    root.title(f"Pi Game ({WIDTH}x{HEIGHT})")
    label = tk.Label(root)
    label.pack()


# ============
# objects
# ============
objects: list[mushitroom_object.MushitroomObject] = []
shit_1 = mushitroom_object.MushitroomObject(1, 2, 413, "black")
objects.append(shit_1)

# ====
# 키보드 이벤트 (Windows에서 Test 하기 위함)
# ====
pressed_keys = set()


def on_key_press(event):
    # 키보드를 누르면 set에 추가 (예: 'w', 'Up', 'space')
    pressed_keys.add(event.keysym)


def on_key_release(event):
    # 키보드를 떼면 set에서 제거
    if event.keysym in pressed_keys:
        pressed_keys.remove(event.keysym)


# keyboard event 바인드
if root is not None:
    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)


def keyboard_event():
    if "Up" in pressed_keys or "w" in pressed_keys:
        print("위")
    if "Down" in pressed_keys or "s" in pressed_keys:
        print("아래")
    if "Left" in pressed_keys or "a" in pressed_keys:
        print("좌")
    if "Right" in pressed_keys or "d" in pressed_keys:
        print("우")


def draw_frame():
    canvas = PIL.Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw_tool = PIL.ImageDraw.Draw(canvas)
    for obj in objects:
        obj.draw(draw_tool)
    return canvas


def main_logic():
    keyboard_event()
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


if __name__ == "__main__":
    main_loop()
    if root is not None:
        root.mainloop()
