import sys
import platform
import time
from PIL import Image, ImageDraw, ImageTk

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
    assholes = db.get_all_users()
except:
    print("DB 연결 실패 혹은 모듈 없음. 더미 데이터 사용.")
    assholes = []

player_name = "Mushitroom"

# ============
# 1. 디바이스(화면) 설정 - OS별 분기
# ============
root = None
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
    root = device.root # 키 바인딩용

else:
    try:
        from luma.core.interface.serial import spi
        from luma.lcd.device import st7789 as lcd_device# 본인 LCD에 맞게 변경 (ili9341 등)
        from gpiozero import Button
        
        # SPI 설정 (핀 번호 확인 필수)
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        device = lcd_device(serial, width=WIDTH, height=HEIGHT, rotate=1)
        print("Luma LCD Device Loaded.")
    except Exception as e:
        print(f"Luma 디바이스 로드 실패: {e}")
        sys.exit(1)


# ============
# 2. 입력(Input) 매니저 - 키보드와 GPIO 통합
# ============
class InputState:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.enter = False
        self.prev = False
        self.next = False
        self.pressed_keys = set() # 윈도우용
        self.just_pressed_keys = set() # 윈도우용 (한번 클릭)

input_state = InputState()

if IS_WINDOWS:
    # [Windows] 키보드 바인딩
    def on_key_press(event):
        sym = event.keysym
        if sym not in input_state.pressed_keys:
            input_state.just_pressed_keys.add(sym)
        input_state.pressed_keys.add(sym)
        
        # 상태 매핑
        if sym in ['Up', 'w']: input_state.up = True
        if sym in ['Down', 's']: input_state.down = True
        if sym in ['Left', 'a']: input_state.left = True
        if sym in ['Right', 'd']: input_state.right = True
        if sym == 'Return': input_state.enter = True
        if sym == 'bracketleft': input_state.prev = True
        if sym == 'bracketright': input_state.next = True

    def on_key_release(event):
        sym = event.keysym
        if sym in input_state.pressed_keys:
            input_state.pressed_keys.remove(sym)
        
        # 상태 해제
        if sym in ['Up', 'w']: input_state.up = False
        if sym in ['Down', 's']: input_state.down = False
        if sym in ['Left', 'a']: input_state.left = False
        if sym in ['Right', 'd']: input_state.right = False
        if sym == 'Return': input_state.enter = False
        if sym == 'bracketleft': input_state.prev = False
        if sym == 'bracketright': input_state.next = False

    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)

else:
    # [Raspberry Pi] GPIO 버튼 바인딩 (핀 번호 수정 필요)
    # 예시: btn_up = Button(17)
    # 여기서는 변수만 매핑합니다. 실제 버튼 객체를 생성하세요.
    # btn_up = Button(17)
    # btn_down = Button(27) 
    # ...
    pass 

def update_input_state_rpi():
    """라즈베리파이에서 GPIO 상태를 읽어 input_state 업데이트"""
    if not IS_WINDOWS:
        # 예시: input_state.up = btn_up.is_pressed
        pass


# ============
# 3. 게임 오브젝트 초기화
# ============
objects = []

shit_1 = mushitroom_object.MushitroomObject(
    x=10, y=10, width=20, height=20, color="black"
)
button_01 = mushitroom_object.MushitroomObject(
    x=100, y=250, width=100, height=50, color="#F0F0F0"
)
button_02 = mushitroom_object.MushitroomObject(
    x=200, y=250, width=100, height=50, color="#FF0000"
)

objects.extend([button_01, button_02, shit_1])

# UI 매니저
ui_manager = MushitroomInterfaceGroup()

btn_adopt = MushitroomInterfaceObject(
    index=0, x=50, y=340, width=120, height=40, color="white", text="adopt", font_weight=FontWeight.HEAVY,
)
btn_nurish = MushitroomInterfaceObject(
    index=0, x=150, y=340, width=120, height=40, color="white", text="nurish", font_weight=FontWeight.HEAVY,
    on_action=lambda: db.create_user("asshole"),
)
btn_dance = MushitroomInterfaceObject(
    index=0, x=200, y=340, width=120, height=40, color="white", text="dance", font_weight=FontWeight.HEAVY,
)
btn_exit = MushitroomInterfaceObject(
    index=1, x=100, y=160, width=120, height=40, color="white", text="EXIT", font_weight=FontWeight.HEAVY,
)
display_money = MushitroomInterfaceObject(
    index=9, x=550, y=20, width=80, height=20, color="#FFFFFF", text=f"money: {100_000}", font_weight=FontWeight.HEAVY,
)

ui_manager.add_element(display_money)
ui_manager.add_element(btn_adopt)
ui_manager.add_element(btn_nurish)
ui_manager.add_element(btn_dance)
ui_manager.add_element(btn_exit)

for i, user in enumerate(assholes):
    ui_manager.add_element(
        MushitroomInterfaceObject(
            index=10,
            x=10,
            y=10 + 30 * i,
            width=200,
            height=25,
            color="#DDDDDD",
            text=f"{user.username} - {user.updated}",
            font_weight=FontWeight.REGULAR,
        )
    )


# ============
# 4. 메인 로직
# ============
def handle_game_logic():
    # RPi일 경우 입력 업데이트
    update_input_state_rpi()

    # 이동 로직 (input_state 사용)
    if input_state.up:
        shit_1.y -= 1
        print("위")
    if input_state.down:
        shit_1.y += 1
        print("아래")
    if input_state.left:
        shit_1.x -= 1
        print("좌")
    if input_state.right:
        shit_1.x += 1
        print("우")

    # 원샷 액션 (Just Pressed)
    if IS_WINDOWS:
        # 윈도우는 just_pressed_keys set 사용
        if "Return" in input_state.just_pressed_keys:
            ui_manager.elements[ui_manager.current_index].on_action()
        if "bracketleft" in input_state.just_pressed_keys:
            ui_manager.select_prev()
        if "bracketright" in input_state.just_pressed_keys:
            ui_manager.select_next()
        
        # 처리 후 초기화
        input_state.just_pressed_keys.clear()
    else:
        # RPi 로직 (Button.is_pressed 등으로 구현 필요)
        pass

def draw_frame() -> Image.Image:
    """화면을 그려서 PIL Image 객체로 반환"""
    # 캔버스 생성
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw_tool = ImageDraw.Draw(canvas)
    
    # 그리기
    ui_manager.draw(draw_tool)
    for obj in objects:
        obj.draw(draw_tool)
        
    return canvas


# ============
# 5. 메인 루프 (OS별 방식 다름)
# ============

def main_loop_windows():
    """Windows용 루프 (Tkinter .after 사용)"""
    handle_game_logic()
    
    # 그리기 및 디스플레이 전송
    pil_image = draw_frame()
    device.display(pil_image) # TkinterEmulator의 display 호출
    
    # 다음 프레임 예약 (FPS 준수)
    root.after(int(FRAME_TIME_SEC * 1000), main_loop_windows)

def main_loop_rpi():
    """RPi용 루프 (While True 사용)"""
    while True:
        start_time = time.time()
        
        handle_game_logic()
        
        pil_image = draw_frame()
        device.display(pil_image) 
        
        # FPS 조절
        elapsed = time.time() - start_time
        sleep_time = max(0, FRAME_TIME_SEC - elapsed)
        time.sleep(sleep_time)

def main():
    if IS_WINDOWS:
        print("Starting Windows Mode (Tkinter Emulator)")
        main_loop_windows()
        root.mainloop()
    else:
        print("Starting RPi Mode (Luma LCD)")
        main_loop_rpi()

if __name__ == "__main__":
    main()