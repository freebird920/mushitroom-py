import sqlite3
import os
import uuid
import src.settings.mushitroom_config as mushitroom_config
import src.schemas.user_schema as schemas
from typing import List, Optional


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

        # ★ 외래키 제약 조건 활성화 (필수)
        conn.execute("PRAGMA foreign_keys = ON;")

        return conn

    def _initialize_db(self):
        """테이블 초기화 (executescript 사용)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.executescript(
                f"""
                -- 1. 유저 정보 (변하지 않는 값)
                CREATE TABLE IF NOT EXISTS {mushitroom_config.TABLE_USER} (
                    id TEXT PRIMARY KEY,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    username TEXT NOT NULL
                );

                -- 2. 게임 상태 (돈, 레벨 등 변하는 값)
                CREATE TABLE IF NOT EXISTS {mushitroom_config.TABLE_GAME_STATE} (
                    id TEXT PRIMARY KEY,
                    money INTEGER DEFAULT 0,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- user_id(외래키)
                    user_id TEXT NOT NULL, 
                    FOREIGN KEY(user_id) REFERENCES {mushitroom_config.TABLE_USER}(id) ON DELETE CASCADE
                );
            """
            )
            conn.commit()
            print("✅ DB 테이블 초기화 완료")
        except Exception as e:
            print(f"❌ DB 초기화 실패: {e}")
        finally:
            conn.close()

    # --- 👇 랭킹 및 점수 관련 메서드 ---

    def add_score(self, user_id: str, score: int):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # 참고: scores 테이블이 _initialize_db에 없어서 에러가 날 수 있음.
            # 필요하다면 _initialize_db에 scores 테이블 생성 구문도 추가해야 함.
            cursor.execute(
                "INSERT INTO scores (user_id, score) VALUES (?, ?)", (user_id, score)
            )
            conn.commit()
            print(f"✅ 점수 저장 완료: 유저({user_id}) - {score}점")
        except Exception as e:
            print(f"❌ 점수 저장 실패: {e}")
        finally:
            conn.close()

    def get_top_rankings(self, limit=10):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = f"""
                SELECT u.username, s.score, s.reg_date
                FROM scores s
                JOIN {mushitroom_config.TABLE_USER} u ON s.user_id = u.id
                ORDER BY s.score DESC 
                LIMIT ?
            """
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def reset_rankings(self):
        """(관리자용) 점수 초기화"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores")
            conn.commit()
            print("⚠ 랭킹이 초기화되었습니다.")
        finally:
            conn.close()

    # --- 👇 유저 생성 및 상태 관리 ---

    def create_user(self, username: str):
        conn = self._get_connection()
        user_id = str(uuid.uuid4())
        try:
            conn.execute(
                f"INSERT INTO {mushitroom_config.TABLE_USER} (id, username) VALUES (?, ?)",
                (user_id, username),
            )
            conn.commit()
            return user_id
        finally:
            conn.close()

    def save_user_state(self, user_id: str, money: int):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 1. 먼저 업데이트를 시도합니다 (이미 게임을 하던 유저일 경우)
            cursor.execute(
                f"""
                UPDATE {mushitroom_config.TABLE_GAME_STATE}
                SET money = ?, updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """,
                (money, user_id),
            )

            # 2. 만약 업데이트된 줄(row)이 0개라면? (신규 유저라 상태 데이터가 없음) -> INSERT
            if cursor.rowcount == 0:
                state_id = str(uuid.uuid4())
                cursor.execute(
                    f"""
                    INSERT INTO {mushitroom_config.TABLE_GAME_STATE} 
                    (id, user_id, money) VALUES (?, ?, ?)
                """,
                    (state_id, user_id, money),
                )
                print(f"✨ 신규 상태 생성: {user_id}")
            else:
                print(f"💾 상태 업데이트: {user_id} (Money: {money})")

            conn.commit()
        except Exception as e:
            print(f"❌ 상태 저장 실패: {e}")
        finally:
            conn.close()

    def get_user_state(self, user_id: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT money FROM {mushitroom_config.TABLE_GAME_STATE}
                WHERE user_id = ?
            """,
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)  # {'money': 1000}
            return None
        finally:
            conn.close()

    def get_all_users(self, limit=50) -> List[schemas.User]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = f"""
                    SELECT 
                        u.id, 
                        u.username, 
                        u.updated
                    FROM {mushitroom_config.TABLE_USER} u
                    ORDER BY u.updated DESC
                    LIMIT ?
                """
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            return [schemas.User(**dict(row)) for row in rows]

        except Exception as e:
            print(f"❌ 유저 목록 조회 실패: {e}")
            return []
        finally:
            conn.close()
