from dataclasses import dataclass
from typing import List


# 1. 유저 정보 모델
@dataclass
class User:
    id: str
    username: str
    updated: str


# 2. 게임 상태 모델
@dataclass
class GameState:
    id: str
    user_id: str
    money: int
    updated: str
    days: int
    mushitrooms: List[str]
