import sqlite3
import os
import uuid
import src.settings.mushitroom_config as mushitroom_config
import src.schemas.user_schema as schemas
from typing import List, Optional


class SqService:
    def __init__(self, db_name="mushitroom.db"):
        self.db_path = os.path.join(os.getcwd(), db_name)
        self._initialize_db()

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
            # 콤마(,) 제거 및 세미콜론(;) 추가, user_id 컬럼 추가 등 문법 오류 수정됨
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
                    id TEXT PRIMARY KEY,  -- 보통 user_id와 동일하게 사용하거나 별도 관리
                    money INTEGER DEFAULT 0,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- user_id(외래키)
                    user_id TEXT NOT NULL, 
                    FOREIGN KEY(user_id) REFERENCES {mushitroom_config.TABLE_USER}(id) ON DELETE CASCADE
                );
                

            """
            )
            conn.commit()
        finally:
            conn.close()

    # --- 👇 랭킹 및 점수 관련 메서드 수정됨 ---

    def add_score(self, user_id: str, score: int):
        """
        점수 저장하기
        - 변경점: username 대신 user_id를 받습니다. (데이터 무결성)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
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
        """
        상위 n개 랭킹 가져오기
        - 변경점: scores 테이블에는 user_id만 있으므로,
          USER_INFO 테이블과 JOIN하여 username을 함께 가져옵니다.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # ★ SQL JOIN 쿼리: 점수 테이블(s)과 유저 테이블(u)을 합침
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

    # --- 👇 편의를 위한 유저 생성 헬퍼 (테스트용) ---
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
        """
        유저의 게임 상태(돈)를 저장합니다.
        - 데이터가 있으면 UPDATE(수정)
        - 데이터가 없으면 INSERT(삽입)
        """
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

            # 2. 만약 업데이트된 줄(row)이 0개라면? (신규 유저라 상태 데이터가 없음)
            # -> 새로 INSERT 합니다.
            if cursor.rowcount == 0:
                state_id = str(uuid.uuid4())  # 상태값의 고유 ID 생성
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
        """유저의 현재 상태(돈)를 가져옵니다."""
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
        """
        [핵심 변경 사항]
        - 반환 타입: List[schemas.UserWithMoney]
        - 순수 User가 아닌 Money가 포함된 확장 모델을 반환합니다.
        """
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

            # **dict(row)로 unpacking 할 때,
            # UserWithMoney 클래스는 id, username, updated, money 모두를 받습니다.
            return [schemas.User(**dict(row)) for row in rows]

        except Exception as e:
            print(f"❌ 유저 목록 조회 실패: {e}")
            return []
        finally:
            conn.close()
