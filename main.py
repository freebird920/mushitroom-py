import sys
import platform
import time
from typing import TYPE_CHECKING

# import pillow
from PIL import Image, ImageDraw

# import settings
from src.settings.mushitroom_config import GPIO_PINS

# import managers
from src.managers import sound_manager
from src.managers.scene_manager import SceneManager, SceneType
from src.managers.input_manager import InputManager


# ============
# 사용자 모듈 임포트
# ============

try:
    import src.settings.mushitroom_config as mushitroom_config
    from src.services.sq_service import SqService
except ImportError as e:
    print(f"필수 모듈을 불러올 수 없습니다: {e}")
    sys.exit(1)

# ============
# 전역 설정
# ============

HEIGHT = mushitroom_config.DISPLAY_HEIGHT
ROTATE = mushitroom_config.DISPLAY_ROTATE
BG_COLOR = mushitroom_config.BG_COLOR
FPS = mushitroom_config.FPS
FRAME_TIME_SEC = 1.0 / FPS
IS_WINDOWS = platform.system() == "Windows"

# ============
# DB & 데이터 설정
# ============
try:
    db = SqService()
except:
    print("DB_ERROR")
    sys.exit(1)

# ============
# 1. 디바이스(화면) 설정
# ============
if TYPE_CHECKING:
    import tkinter as tk
root: "tk.Tk | None" = None
device: "TkinterEmulator | st7789 |None" = None


# ============
# WINDOWS 설정
# ============
if IS_WINDOWS:
    import tkinter as tk
    from PIL import ImageTk
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

    class TkinterEmulator:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.root = tk.Tk()
            self.root.title("MUSHITROOM (Tkinter Emulator)")
            self.label = tk.Label(self.root)
            self.label.pack()
            self.root.geometry(f"{width}x{height}")
            self.root.focus_set()

        def display(self, pil_image):
            # PIL 이미지를 Tkinter용으로 변환하여 라벨에 업데이트
            self.tk_image = ImageTk.PhotoImage(pil_image)
            self.label.config(image=self.tk_image)

        def update_gui(self):
            # Tkinter 이벤트 루프 처리
            self.root.update()
            self.root.update_idletasks()

    device = TkinterEmulator(
        width=mushitroom_config.DISPLAY_WIDTH, height=mushitroom_config.DISPLAY_HEIGHT
    )
    root = device.root  # 키 바인딩용

else:
    # =================================================
    # [Raspberry Pi 설정] ST7789V 2.4인치 (240x320)
    # =================================================
    try:
        from luma.core.interface.serial import spi
        from luma.lcd.device import st7789  # 정확한 모델명 사용
        from gpiozero import PWMLED

        backlight = PWMLED(GPIO_PINS.BACKLIGHT_PWM.value)
        backlight.value = 0.8

        # 1. SPI 설정 (아까 성공한 핀맵)
        # port=0, device=0 -> SPI0
        # DC=GPIO 24, RST=GPIO 25
        serial = spi(
            port=0,
            device=0,
            gpio_DC=mushitroom_config.GPIO_PINS.DISPLAY_DC.value,
            gpio_RST=mushitroom_config.GPIO_PINS.DISPLAY_RST.value,
            bus_speed_hz=mushitroom_config.SPI_SPEED,
        )

        # 2. 디바이스 초기화 (중요: width, height, rotate 명시)
        # 2.4인치 240x320 꽉 채우기
        device = st7789(
            serial, width=mushitroom_config.DISPLAY_WIDTH, height=HEIGHT, rotate=ROTATE
        )
        print(f"Luma LCD Device Loaded: {mushitroom_config.DISPLAY_WIDTH}x{HEIGHT}")

    except Exception as e:
        print(f"Luma 디바이스 로드 실패: {e}")
        sys.exit(1)


# ============
# manager 호출
# ============

sound_manager = sound_manager.SoundManager()
scene_manager = SceneManager(db)
input_manager = InputManager(IS_WINDOWS, root)
scene_manager.switch_scene(SceneType.SELECT_USER)


# ============
# 5. 메인 루프 (OS별 방식 다름)
# ============


# ============
# 메인 루프
# ============
def handle_game_logic():
    scene_manager.handle_input(input_manager.state)
    scene_manager.update()
    input_manager.clear_just_pressed()


def draw_frame() -> Image.Image:
    canvas = Image.new(
        "RGBA",
        (
            mushitroom_config.DISPLAY_WIDTH,
            mushitroom_config.DISPLAY_HEIGHT,
        ),
        BG_COLOR,
    )
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
        root.after(
            int(FRAME_TIME_SEC * 1000),
            main_loop_windows,
        )


def main_loop_rpi():

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
