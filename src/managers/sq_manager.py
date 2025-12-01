import sqlite3
import os
import uuid
import json
from typing import List, Optional, Dict, Any

# 설정 파일 및 스키마 임포트 (경로는 프로젝트에 맞게 확인해주세요)
from schemas.mushitroom_schema import MushitroomSchema
import src.settings.mushitroom_config as mushitroom_config
import src.schemas.user_schema as schemas


class SqService:
    # [Singleton 1] 인스턴스를 저장할 클래스 변수
    _instance: Optional["SqService"] = None

    # [Singleton 2] 인스턴스 생성 제어
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name="mushitroom.db"):
        # [Singleton 3] 초기화 중복 방지 (최초 1회만 실행)
        if hasattr(self, "initialized"):
            return

        print(f"[System] DB 서비스 초기화 (Singleton) - {db_name}")
        self.db_path = os.path.join(os.getcwd(), db_name)

        # 테이블 생성도 딱 한 번만 수행됨
        self._initialize_db()

        # 초기화 완료 플래그
        self.initialized = True

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # --- 🚀 라즈베리 파이 제로 2 최적화 ---
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA cache_size=-4000;")

        # 외래키 제약 조건 활성화
        conn.execute("PRAGMA foreign_keys = ON;")

        return conn

    def _initialize_db(self):
        """
        테이블 초기화
        Dataclass 구조에 맞춰 스키마를 업데이트했습니다.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.executescript(
                f"""
                -- 1. 유저 정보 (User)
                CREATE TABLE IF NOT EXISTS {mushitroom_config.TABLE_USER} (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- 2. 게임 상태 (GameState)
                -- days 컬럼 추가됨
                CREATE TABLE IF NOT EXISTS {mushitroom_config.TABLE_GAME_STATE} (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    money INTEGER DEFAULT 0,
                    days INTEGER DEFAULT 1,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES {mushitroom_config.TABLE_USER}(id) ON DELETE CASCADE
                );

                -- 3. 버섯 정보 (Mushitroom)
                -- GameState의 mushitrooms 리스트는 1:N 관계이므로 별도 테이블로 분리합니다.
                CREATE TABLE IF NOT EXISTS {mushitroom_config.TABLE_MUSHITROOM} (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    age INTEGER DEFAULT 0,
                    exp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    health INTEGER DEFAULT 100,
                    talent INTEGER DEFAULT 0,
                    cute INTEGER DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES {mushitroom_config.TABLE_USER}(id) ON DELETE CASCADE
                );
                
                -- 4. 랭킹 (Scores) - 필요 시 사용
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES {mushitroom_config.TABLE_USER}(id) ON DELETE CASCADE
                );
                """
            )
            conn.commit()
            print("✅ DB 테이블 스키마 초기화 완료 (User, GameState, Mushitroom)")
        except Exception as e:
            print(f"❌ DB 초기화 실패: {e}")
        finally:
            conn.close()

    # --- 👇 유저 및 상태 관리 메서드 ---

    def create_user(self, username: str) -> str | None:
        """새 유저를 생성하고 user_id를 반환합니다."""
        conn = self._get_connection()
        user_id = str(uuid.uuid4())
        try:
            conn.execute(
                f"INSERT INTO {mushitroom_config.TABLE_USER} (id, username) VALUES (?, ?)",
                (user_id, username),
            )
            # 유저 생성 시 기본 게임 상태도 같이 만들어주면 좋습니다.
            self._init_game_state(conn, user_id)

            conn.commit()
            return user_id
        except Exception as e:
            print(f"❌ 유저 생성 실패: {e}")
            return None
        finally:
            conn.close()

    def _init_game_state(self, conn, user_id: str):
        """내부 호출용: 유저 생성 시 초기 게임 상태 생성"""
        state_id = str(uuid.uuid4())
        conn.execute(
            f"""
            INSERT INTO {mushitroom_config.TABLE_GAME_STATE} 
            (id, user_id, money, days) VALUES (?, ?, ?, ?)
            """,
            (state_id, user_id, 0, 1),  # 초기 돈 0, 1일차
        )

    def save_game_state(self, user_id: str, money: int, days: int):
        """
        게임 상태(돈, 날짜)를 저장합니다.
        GameState Dataclass의 필드를 반영합니다.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE {mushitroom_config.TABLE_GAME_STATE}
                SET money = ?, days = ?, updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (money, days, user_id),
            )
            if cursor.rowcount == 0:
                print(
                    f"⚠ 경고: 해당 유저({user_id})의 게임 상태가 없어 업데이트되지 않았습니다."
                )
            else:
                conn.commit()
                # print(f"💾 상태 저장 완료: {user_id} (Money: {money}, Days: {days})")
        except Exception as e:
            print(f"❌ 게임 상태 저장 실패: {e}")
        finally:
            conn.close()

    def save_mushitroom(self, user_id: str, mush_data: MushitroomSchema):
        """
        개별 버섯 정보를 저장하거나 업데이트합니다 (UPSERT 개념).
        mush_data는 Mushitroom Dataclass 객체여야 합니다.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 먼저 업데이트 시도
            cursor.execute(
                f"""
                UPDATE {mushitroom_config.TABLE_MUSHITROOM}
                SET name=?, age=?, exp=?, level=?, health=?, talent=?, cute=?
                WHERE id=? AND user_id=?
                """,
                (
                    mush_data.name,
                    mush_data.age,
                    mush_data.exp,
                    mush_data.level,
                    mush_data.health,
                    mush_data.talent,
                    mush_data.cute,
                    mush_data.id,
                    user_id,
                ),
            )

            # 없으면 생성 (Insert)
            if cursor.rowcount == 0:
                cursor.execute(
                    f"""
                    INSERT INTO {mushitroom_config.TABLE_MUSHITROOM}
                    (id, user_id, name, created, age, exp, level, health, talent, cute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mush_data.id,
                        user_id,
                        mush_data.name,
                        mush_data.created,
                        mush_data.age,
                        mush_data.exp,
                        mush_data.level,
                        mush_data.health,
                        mush_data.talent,
                        mush_data.cute,
                    ),
                )
                print(f"🍄 새 버섯 등록: {mush_data.name}")

            conn.commit()
        except Exception as e:
            print(f"❌ 버섯 저장 실패: {e}")
        finally:
            conn.close()

    def get_full_game_state(self, user_id: str) -> Optional[schemas.GameState]:
        """
        [핵심] DB에서 데이터를 긁어모아 GameState Dataclass 형태로 반환합니다.
        GameState.mushitrooms는 버섯들의 ID 리스트(List[str])를 가집니다.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 1. GameState 기본 정보 조회
            cursor.execute(
                f"SELECT * FROM {mushitroom_config.TABLE_GAME_STATE} WHERE user_id = ?",
                (user_id,),
            )
            state_row = cursor.fetchone()
            if not state_row:
                return None

            state_dict = dict(state_row)

            # 2. 해당 유저의 모든 버섯 ID 조회
            cursor.execute(
                f"SELECT id FROM {mushitroom_config.TABLE_MUSHITROOM} WHERE user_id = ?",
                (user_id,),
            )
            mush_rows = cursor.fetchall()

            # 버섯 ID들을 리스트로 변환 (GameState.mushitrooms: List[str])
            mush_ids = [row["id"] for row in mush_rows]

            # 3. Dataclass 매핑
            # DB 컬럼과 Dataclass 필드명이 일치한다고 가정
            return schemas.GameState(
                id=state_dict["id"],
                user_id=state_dict["user_id"],
                money=state_dict["money"],
                days=state_dict["days"],
                updated=state_dict["updated"],
                mushitrooms=mush_ids,  # ID 리스트 주입
            )

        except Exception as e:
            print(f"❌ 게임 데이터 로드 실패: {e}")
            return None
        finally:
            conn.close()

    def get_mushitroom(self, mush_id: str) -> Optional[MushitroomSchema]:
        """버섯 ID로 버섯 상세 정보를 가져옵니다."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM {mushitroom_config.TABLE_MUSHITROOM} WHERE id = ?",
                (mush_id,),
            )
            row = cursor.fetchone()
            if row:
                # Row 객체를 dict로 변환 후 Dataclass 생성
                # (주의: created 같은 timestamp 필드는 DB에서 문자열로 오므로 변환 필요 시 처리)
                return MushitroomSchema(**dict(row))
            return None
        finally:
            conn.close()

    def get_all_users(self, limit: int = 50) -> List[schemas.User]:
        """
        모든 유저 목록을 가져와 User Dataclass 리스트로 반환합니다.
        :param limit: 가져올 최대 유저 수 (기본 50명)
        :return: List[schemas.User]
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # User Dataclass 필드(id, username, updated)와 순서/이름을 맞춰 조회
            query = f"""
                SELECT id, username, updated
                FROM {mushitroom_config.TABLE_USER}
                ORDER BY updated DESC
                LIMIT ?
            """
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            # sqlite3.Row -> dict -> User Dataclass로 변환
            # (**dict(row)는 딕셔너리의 키-값을 인자로 풀어서 넣어줍니다)
            return [schemas.User(**dict(row)) for row in rows]

        except Exception as e:
            print(f"❌ 유저 목록 조회 실패: {e}")
            return []
        finally:
            conn.close()
