from enum import Enum


class ObjectType(Enum):
    MUSHITROOM = "MUSHITROOM"
    DEFAULT = "DEFAULT"
    INTERFACE = "INTERFACE"


class FontWeight(Enum):
    # (Enum 이름) = (실제 파일명)
    # assets 폴더 안에 이 파일들이 실제로 있어야 합니다.
    LIGHT = "NanumSquareNeo-aLt.ttf"
    REGULAR = "NanumSquareNeo-bRg.ttf"
    BOLD = "NanumSquareNeo-cBd.ttf"
    EXTRA_BOLD = "NanumSquareNeo-dEb.ttf"
    HEAVY = "NanumSquareNeo-eHv.ttf"
