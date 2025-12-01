from dataclasses import dataclass


@dataclass
class MushitroomSchema:
    id: str
    created: str
    name: str
    age: int
    exp: int
    level: int
    health: int
    talent: int
    cute: int
