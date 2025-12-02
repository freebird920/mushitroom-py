# ===
# 기본 설정
# ===

from enum import IntEnum

ZOOM_IN : int = 1
DISPLAY_WIDTH: int = 320 * ZOOM_IN 
DISPLAY_HEIGHT: int = 240 * ZOOM_IN
DISPLAY_ROTATE: int = 2
BG_COLOR = "white"
FPS: int = 24
SPI_SPEED = 48 * 1_000 * 1_000


# ============
# GPIO PIN OUT
# ============
class GPIO_PINS(IntEnum):
    DISPLAY_DC = 24
    DISPLAY_RST = 25
    BACKLIGHT_PWM = 18
    BUTTON_UP = 20
    BUTTON_DOWN = 21
    BUTTON_RETURN = 26

    def __init__(self, value):
        if not isinstance(value, int):
            raise ValueError(
                f"GPIO 핀 번호는 반드시 정수(int)여야 합니다. 잘못된 값: {value} ({type(value)})"
            )


BUTTON_BOUNCE_TIME = 0.015

# ===
TABLE_USER: str = "USER_INFO"
TABLE_GAME_STATE: str = "GAME_STATE"
TABLE_MUSHITROOM = "mushitrooms"
# ===
