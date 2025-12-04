from enum import Enum, auto


class SceneType(Enum):
    LOBBY_SCENE = auto()
    SELECT_USER = auto()
    SELECT_MUSHROOM = auto()
    USER_TEST = auto()
    GAME_PLAY = auto()
    ENDING = auto()
    PHISHING = auto()
    TITLE_SCENE = auto()
    FEED_SCENE = auto()
    GOEHA_TIME = auto()


class ObjectType(Enum):
    MUSHITROOM = "MUSHITROOM"
    DEFAULT = "DEFAULT"
    INTERFACE = "INTERFACE"


class FontStyle(Enum):
    LIGHT = "NanumSquareNeo-aLt.ttf"
    REGULAR = "NanumSquareNeo-bRg.ttf"
    BOLD = "NanumSquareNeo-cBd.ttf"
    EXTRA_BOLD = "NanumSquareNeo-dEb.ttf"
    HEAVY = "NanumSquareNeo-eHv.ttf"
    COOKIE_BOLD = "CookieRun-Bold.ttf"


class InputActions(Enum):
    DOWN = "down"
    UP = "up"
    RIGHT = "right"
    LEFT = "left"
    PREV = "prev"
    NEXT = "next"
    ENTER = "enter"
    ESCAPE = "escape"
