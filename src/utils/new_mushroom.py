from datetime import datetime
import uuid
from classes.mushroom_class import MushroomType
from managers.sq_manager import SqManager
from schemas.mushitroom_schema import MushitroomSchema
from utils.name_after_mushitroom import MushroomNameGenerator


def new_mushroom(user_id: str, mushroom_type: MushroomType):
    """버섯 입양 로직"""
    print("🍄 버섯 입양 시도...")
    db = SqManager()
    if user_id is None:
        return

    if db.count_alive_mushrooms(user_id) >= 3:
        print("⚠️ 버섯은 최대 3마리까지만 키울 수 있습니다.")
        return

    new_mush_id = str(uuid.uuid4())
    now_str = datetime.now().isoformat()

    new_mushroom = MushitroomSchema(
        user_id=user_id,
        id=new_mush_id,
        created=now_str,
        type=mushroom_type,
        name=MushroomNameGenerator().get_random_name(name=mushroom_type.name_kr),
        age=0,
        exp=0,
        level=1,
        health=100,
        strong=10
        talent=5,
        cute=10,
        is_alive=True,
    )

    return db.save_mushitroom(user_id=user_id, mush_data=new_mushroom)
