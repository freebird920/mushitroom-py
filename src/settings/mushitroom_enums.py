from enum import Enum, auto


class SceneType(Enum):
    SELECT_USER = auto()
    USER_TEST = auto()
    GAME_PLAY = auto()
    ENDING = auto()
    PHISHING = auto()


class ObjectType(Enum):
    MUSHITROOM = "MUSHITROOM"
    DEFAULT = "DEFAULT"
    INTERFACE = "INTERFACE"


class FontWeight(Enum):
    LIGHT = "NanumSquareNeo-aLt.ttf"
    REGULAR = "NanumSquareNeo-bRg.ttf"
    BOLD = "NanumSquareNeo-cBd.ttf"
    EXTRA_BOLD = "NanumSquareNeo-dEb.ttf"
    HEAVY = "NanumSquareNeo-eHv.ttf"
