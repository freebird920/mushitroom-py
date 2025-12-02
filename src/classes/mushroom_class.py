from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.mushitroom_schema import MushitroomSchema


# 1. Enum 정의
class MushroomType(Enum):
    # (영문명, 한글명, 이미지 경로)
    GOMBO = ("Morel", "곰보버섯", "assets/images/gombo.png", "gombo")
    MAGUI = ("Devil's Bolete", "마귀버섯", "assets/images/magui.png", "magui")

    def __init__(self, name_en: str, name_kr: str, image_path: str, image_name: str):
        self.name_en = name_en
        self.name_kr = name_kr
        self.image_path = image_path
        self.image_name = image_name

    @classmethod
    def from_str(cls, value: str):
        """문자열(Key 또는 한글명)을 받아서 Enum 객체를 반환하는 만능 함수"""
        # 1. "GOMBO" 같은 Key로 찾기
        try:
            return cls[value]
        except KeyError:
            pass

        # 2. "곰보버섯" 같은 한글명으로 찾기
        for member in cls:
            if member.name_kr == value:
                return member
        return None


# 2. 로직 클래스 (행동 담당)
class MushroomClass:
    def __init__(self, schema: "MushitroomSchema") -> None:
        # 스키마를 통째로 '참조'합니다. (자동 연동됨)
        self.data = schema

    def eat_food(self):
        print(f"{self.data.name}이(가) 밥을 먹습니다.")
        # 여기서 self.data를 수정하면 원본 스키마도 수정됩니다.
        self.data.health += 10
        self.data.exp += 5

    def attack(self):
        print(f"공격! (현재 레벨: {self.data.level})")
