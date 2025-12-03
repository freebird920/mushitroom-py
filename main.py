try:
    # ===============================================
    # src 경로 인식을 위한 코드
    # ===============================================

    import sys
    import os
    import traceback

    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, "src")
    if src_path not in sys.path:
        sys.path.append(src_path)

    # 프로젝트 모듈은 이 아래에서 부터 import
    # ===============================================

    # =========
    # 외부 라이브러리 import
    # =========
    import time
    import platform
    from PIL import Image, ImageDraw

    # ===================
    # 프로젝트 모듈 import
    # ===================
    from settings.mushitroom_config import GPIO_PINS
    from managers.audio_manager import AudioManager
    from managers.scene_manager import SceneManager, SceneType
    from managers.input_manager import InputManager
    from managers.timer_manager import TimerManager
    import settings.mushitroom_config as mushitroom_config
    from managers.sq_manager import SqService

except ImportError as e:

    print(f"필수 모듈 로드 실패: {e} 3초 후 종료됩니다.")

    import time

    time.sleep(3)
    sys.exit(1)

# ============
# 전역 설정
# ============
HEIGHT = mushitroom_config.DISPLAY_HEIGHT
ROTATE = mushitroom_config.DISPLAY_ROTATE
BG_COLOR = mushitroom_config.BG_COLOR
FPS = mushitroom_config.FPS
FRAME_TIME_SEC = 1.0 / FPS
# win32도 포함해야 안전함
IS_WINDOWS = platform.system() == "Windows" or platform.system() == "Win32"

# ============
# 전역 변수 (초기화는 main에서)
# ============
db = None
timer_manager = None
sound_manager = None
scene_manager = None
input_manager = None
root = None
device = None


# ============
# 메인 루프 함수들
# ============
def handle_game_logic():
    global scene_manager, input_manager
    if scene_manager:
        scene_manager.handle_input()
    if scene_manager:
        scene_manager.update()
    if input_manager:
        input_manager.clear_just_pressed()


def draw_frame() -> Image.Image:
    global scene_manager
    canvas = Image.new(
        "RGBA",
        (mushitroom_config.DISPLAY_WIDTH, mushitroom_config.DISPLAY_HEIGHT),
        BG_COLOR,
    )
    draw_tool = ImageDraw.Draw(canvas)
    if scene_manager:
        scene_manager.draw(draw_tool)
    return canvas


def main_loop_windows():
    global root, device
    handle_game_logic()
    pil_image = draw_frame()

    if device is not None and root is not None:
        device.display(pil_image)
        # Tkinter 이벤트 루프에 다시 예약
        root.after(int(FRAME_TIME_SEC * 1000), main_loop_windows)


def main_loop_rpi():
    global device
    while True:
        start_time = time.time()
        handle_game_logic()
        pil_image = draw_frame()
        if device is not None:
            device.display(pil_image)
        elapsed = time.time() - start_time
        sleep_time = max(0, FRAME_TIME_SEC - elapsed)
        time.sleep(sleep_time)


# ============
# 메인 함수 (모든 import와 초기화를 여기로 이동)
# ============
def main():
    global db, timer_manager, sound_manager, scene_manager, input_manager, root, device

    try:
        print(">>> 프로그램 초기화 시작...")

        # 1. DB 연결
        db = SqService()

        # 2. 화면(Device) 설정
        if IS_WINDOWS:
            print("Mode: Windows (Emulator)")
            # ★★★ 여기서 import 하면 빨간 줄 사라짐 ★★★
            import tkinter as tk
            from PIL import ImageTk
            import ctypes

            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass

            # 클래스도 여기서 정의 (scope 문제 해결)
            class TkinterEmulator:
                def __init__(self, width, height):
                    self.width = width
                    self.height = height
                    self.root = tk.Tk()
                    self.root.title("MUSHITROOM Emulator")
                    self.label = tk.Label(self.root)
                    self.label.pack()
                    self.root.geometry(f"{width}x{height}")
                    self.root.focus_set()

                def display(self, pil_image):
                    self.tk_image = ImageTk.PhotoImage(pil_image)
                    self.label.config(image=self.tk_image)

            # 디바이스 생성
            device = TkinterEmulator(
                width=mushitroom_config.DISPLAY_WIDTH,
                height=mushitroom_config.DISPLAY_HEIGHT,
            )
            root = device.root

            # 아이콘 설정
            icon_path = os.path.join(src_path, "assets", "images", "salgu3.png")
            if os.path.exists(icon_path):
                try:
                    icon = tk.PhotoImage(file=icon_path)
                    root.iconphoto(False, icon)
                except Exception as e:
                    print(f"아이콘 로드 실패: {e}")

        else:
            print("Mode: Raspberry Pi (Luma LCD)")
            # ★★★ 라즈베리파이용 import도 여기로 이동 ★★★
            from luma.core.interface.serial import spi
            from luma.lcd.device import st7789
            from gpiozero import PWMLED

            backlight = PWMLED(GPIO_PINS.BACKLIGHT_PWM.value)
            backlight.value = 0.8

            serial = spi(
                port=0,
                device=0,
                gpio_DC=mushitroom_config.GPIO_PINS.DISPLAY_DC.value,
                gpio_RST=mushitroom_config.GPIO_PINS.DISPLAY_RST.value,
                bus_speed_hz=mushitroom_config.SPI_SPEED,
            )
            device = st7789(
                serial,
                width=mushitroom_config.DISPLAY_WIDTH,
                height=HEIGHT,
                rotate=ROTATE,
            )

        # 3. 매니저 초기화
        timer_manager = TimerManager()
        timer_manager.start()

        sound_manager = AudioManager()
        sound_manager.set_bgm_volume(25)
        sound_manager.set_sfx_volume(100)
        sound_manager.set_main_volume(50)

        scene_manager = SceneManager()
        input_manager = InputManager(is_windows=IS_WINDOWS, root=root)

        scene_manager.switch_scene(SceneType.TITLE_SCENE)

        # 4. 루프 시작
        print(">>> 메인 루프 진입")
        if IS_WINDOWS:
            main_loop_windows()
            if root is not None:
                root.mainloop()
        else:
            main_loop_rpi()

    except Exception as e:
        print("\n" + "!" * 40)
        print("   [CRITICAL ERROR] 오류 발생")
        print("!" * 40 + "\n")
        traceback.print_exc()
        print("\n" + "=" * 40)
        input("엔터 키를 누르면 종료합니다...")


if __name__ == "__main__":
    main()
