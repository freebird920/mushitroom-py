import sqlite3
import os


class SqService:
    def __init__(self, db_name="mushitroom.db"):
        # DB 파일 경로 설정 (실행 파일이 있는 위치 기준)
        # .pyz로 묶어도 데이터는 바깥에 저장되어야 하므로 os.getcwd() 사용 권장
        self.db_path = os.path.join(os.getcwd(), db_name)
        self._initialize_db()

    def _get_connection(self):
        """DB 연결을 만들어주는 내부 함수"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        """테이블이 없으면 생성"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
        finally:
            conn.close()

    def add_score(self, username: str, score: int):
        """점수 저장하기"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO scores (username, score) VALUES (?, ?)", (username, score)
            )
            conn.commit()
            print(f"✅ 점수 저장 완료: {username} - {score}점")
        except Exception as e:
            print(f"❌ 점수 저장 실패: {e}")
        finally:
            conn.close()

    def get_top_rankings(self, limit=10):
        """상위 n개 랭킹 가져오기 (리스트 + 딕셔너리 형태 반환)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scores ORDER BY score DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()

            # sqlite3.Row 객체를 일반 dict로 변환해서 반환 (쓰기 편하게)
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def reset_rankings(self):
        """(관리자용) 점수 초기화"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scores")  # 데이터만 날림
            conn.commit()
            print("⚠ 랭킹이 초기화되었습니다.")
        finally:
            conn.close()
