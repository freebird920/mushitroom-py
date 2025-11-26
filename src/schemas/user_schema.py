from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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


# 3. 랭킹 정보 모델 (UI 표시용)
@dataclass
class RankingEntry:
    username: str
    score: int
    reg_date: str
