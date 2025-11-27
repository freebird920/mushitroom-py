import sys
import platform
import time
from PIL import Image, ImageDraw, ImageTk
from typing import TYPE_CHECKING

# [수정됨] 실제 파일 경로와 이름에 맞춰 import 경로 수정
# 파일명: src/scenes/select_user_scene.py -> 모듈명: src.scenes.select_user_scene
from src.classes.scene_base import BaseScene
from src.scenes.select_user_scene import SelectUserScene

# 파일명: src/classes/input_manager.py -> 모듈명: src.classes.input_manager
from src.classes.input_manager import InputManager

# ============
# 사용자 모듈 임포트
# ============

try:
    import src.settings.mushitroom_config as mushitroom_config
    from src.settings.mushitroom_enums import FontWeight
    import src.classes.mushitroom_object as mushitroom_object
    from src.classes.mushitroom_interface_object import MushitroomInterfaceObject
    from src.classes.mushitroom_interface_object import MushitroomInterfaceGroup
    from src.services.sq_service import SqService
except ImportError as e:
    print(f"필수 모듈을 불러올 수 없습니다: {e}")
    sys.exit(1)

# ============
# 전역 설정
# ============
WIDTH = mushitroom_config.DISPLAY_WIDTH
HEIGHT = mushitroom_config.DISPLAY_HEIGHT
BG_COLOR = mushitroom_config.BG_COLOR
FPS = mushitroom_config.FPS
FRAME_TIME_SEC = 1.0 / FPS
IS_WINDOWS = platform.system() == "Windows"

# ============
# DB & 데이터 설정
# ============
try:
    db = SqService()
    # assholes 변수는 user select scene에서 로드하므로 여기선 제거하거나 유지
    assholes = db.get_all_users()
except:
    print("DB_ERROR")
    sys.exit(1)

# ============
# 1. 디바이스(화면) 설정 - OS별 분기
# ============
if TYPE_CHECKING:
    import tkinter as tk
root: "tk.Tk | None" = None
device = None

if IS_WINDOWS:
    import tkinter as tk

    class TkinterEmulator:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.root = tk.Tk()
            self.root.title("MUSHITROOM (Tkinter Emulator)")
            self.label = tk.Label(self.root)
            self.label.pack()
            self.root.geometry(f"{width}x{height}")
            # 키보드 포커스
            self.root.focus_set()

        def display(self, pil_image):
            # PIL 이미지를 Tkinter용으로 변환하여 라벨에 업데이트
            self.tk_image = ImageTk.PhotoImage(pil_image)
            self.label.config(image=self.tk_image)

        def update_gui(self):
            # Tkinter 이벤트 루프 처리
            self.root.update()
            self.root.update_idletasks()

    device = TkinterEmulator(WIDTH, HEIGHT)
    root = device.root  # 키 바인딩용

else:
    try:
        from luma.core.interface.serial import spi
        from luma.lcd.device import (
            st7789 as lcd_device,
        )  # 본인 LCD에 맞게 변경 (ili9341 등)
        from gpiozero import Button

        # SPI 설정 (핀 번호 확인 필수)
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        device = lcd_device(serial, width=WIDTH, height=HEIGHT, rotate=1)
        print("Luma LCD Device Loaded.")
    except Exception as e:
        print(f"Luma 디바이스 로드 실패: {e}")
        sys.exit(1)


# ============
# Scene Manager
# ============
class SceneManager:

    def __init__(self, db_instance):
        self.current_scene = None
        self.db = db_instance

    def switch_scene(self, new_scene: BaseScene):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = new_scene
        self.current_scene.on_enter()

    def handle_input(self, input_state):
        if self.current_scene:
            self.current_scene.handle_input(input_state)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self, draw_tool):
        if self.current_scene:
            self.current_scene.draw(draw_tool)


# 로컬 클래스 사용
scene_manager = SceneManager(db)

# InputManager 초기화 (src.classes.input_manager)
input_manager = InputManager(IS_WINDOWS, root)

# 초기 씬 설정
scene_manager.switch_scene(SelectUserScene(scene_manager, db))


# ============
# 5. 메인 루프 (OS별 방식 다름)
# ============


# ============
# 메인 루프
# ============
def handle_game_logic():
    # 1. 입력 상태 업데이트 (RPi 폴링 등)
    input_manager.update()

    # 2. 씬에 입력 전달
    scene_manager.handle_input(input_manager.state)

    # 3. 게임 로직 업데이트
    scene_manager.update()

    # 4. 프레임 종료 전 Just Pressed 상태 초기화
    input_manager.clear_just_pressed()


def draw_frame() -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw_tool = ImageDraw.Draw(canvas)
    scene_manager.draw(draw_tool)
    return canvas


def main_loop_windows():
    """Windows용 루프 (Tkinter .after 사용)"""
    handle_game_logic()

    # 그리기 및 디스플레이 전송
    pil_image = draw_frame()
    if device is not None and root is not None:
        device.display(pil_image)

        # 다음 프레임 예약 (FPS 준수)
        root.after(int(FRAME_TIME_SEC * 1000), main_loop_windows)


def main_loop_rpi():
    """RPi용 루프 (While True 사용)"""
    while True:
        start_time = time.time()

        handle_game_logic()

        pil_image = draw_frame()
        if device is not None:
            device.display(pil_image)

        # FPS 조절
        elapsed = time.time() - start_time
        sleep_time = max(0, FRAME_TIME_SEC - elapsed)
        time.sleep(sleep_time)


def main():
    if IS_WINDOWS:
        print("Starting Windows Mode (Tkinter Emulator)")
        main_loop_windows()
        if root is not None:
            root.mainloop()
    else:
        print("Starting RPi Mode (Luma LCD)")
        main_loop_rpi()


if __name__ == "__main__":
    main()
