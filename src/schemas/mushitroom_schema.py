from dataclasses import dataclass
from optparse import Option
from typing import Optional

# [중요] MushroomType이 정의된 위치에서 import 해야 합니다.
# 만약 circular import 에러가 난다면, MushroomType을 별도 파일(enums.py)로 옮기는 게 좋습니다.
from classes.mushroom_class import MushroomType


@dataclass
class MushitroomSchema:
    id: str
    user_id: str
    created: str
    name: str
    type: Optional[MushroomType] = None  # DB에서 읽을 땐 str, 쓸 땐 Enum

    age: int = 0
    exp: int = 0
    level: int = 1
    health: int = 100
    talent: int = 0
    cute: int = 0
    is_alive: Optional[bool] = True

    def __post_init__(self):
        if isinstance(self.is_alive, int):
            self.is_alive = bool(self.is_alive)
        # 1. [핵심 수정] DB에서 문자열("GOMBO")로 들어왔다면 -> Enum으로 변환
        if isinstance(self.type, str):
            # from_str 메서드가 없다면 MushroomType[self.type] 사용
            found = MushroomType.from_str(self.type)
            if found:
                self.type = found
            else:
                print(f"⚠ 알 수 없는 타입 문자열: {self.type}")
                self.type = None  # 혹은 기본값
        if self.type is None:
            found = MushroomType.from_str(self.name)
            if found:
                self.type = found
            else:
                self.type = MushroomType.GOMBO

        if self.type and hasattr(self.type, "name"):
            # 필요하다면 여기서 추가 로직 수행
            pass
