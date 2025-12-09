import random  # 1. random 모듈 임포트
from enum import Enum


class MushroomType(Enum):
    # (영문명, 한글명, 이미지 경로, 이미지 이름)
    GOMBO = ("Morel", "곰보버섯", "assets/images/gombo.png", "gombo")
    MAGUI = ("Devil's Bolete", "마귀광대버섯", "assets/images/magui.png", "magui")
    DALGYAL = ("DALGYAL", "달걀버섯", "assets/images/dalgyal.png", "dalgyal")
    GWANG = ("GWANG", "광대버섯", "assets/images/dalgyal.png", "gwang")
    SASUM = ("SASUM", "붉은뿔사슴버섯", "assets/images/dalgyal.png", "sasum")
    SALGU = ("SALGU", "살구버섯", "", "salgu")
    HWANGUM = ("HWANGUM", "황금등불버섯", "HWANGUM", "hwangum")
    PYOGO = ("PYOGO", "표고버섯", "PYOGO", "pyogo")

    def __init__(self, name_en: str, name_kr: str, image_path: str, image_name: str):
        self.name_en = name_en
        self.name_kr = name_kr
        self.image_path = image_path
        self.image_name = image_name

    @classmethod
    def from_str(cls, value: str):
        try:
            return cls[value]
        except KeyError:
            pass
        for member in cls:
            if member.name_kr == value:
                return member
        return None

    # ▼▼▼ 추가된 부분 ▼▼▼
    @classmethod
    def get_random(cls):
        """Enum 멤버 중 하나를 무작위로 반환"""
        return random.choice(list(cls))
