# MUSHITROOM

- [MUSHITROOM](#mushitroom)
  - [python 설정](#python-설정)
    - [python uv 설정](#python-uv-설정)
    - [python .venv 설정](#python-venv-설정)
  - [windows를 위한 설정](#windows를-위한-설정)
  - [기본 세팅](#기본-세팅)
  - [main.py](#mainpy)
    - [objects](#objects)
    - [키보드 이벤트](#키보드-이벤트)
  - [mushitroom\_config.py](#mushitroom_configpy)
  - [SQLite 데이터베이스](#sqlite-데이터베이스)
    - [1. 개요](#1-개요)
    - [2. 파이썬에서 사용법](#2-파이썬에서-사용법)

## python 설정

### python uv 설정

- 프로젝트 초기화

    ```bash
    uv sync
    ```

- 패키지 설치

    ```bash
    uv add [패키지명]
    ```

### python .venv 설정

- venv 초기화

    ```bash
    python -m venv .venv
    ```

- venv 활성화

    ```bash
    # windows
    .venv\Scripts\activate

    # linux
    source .venv/bin/activate
    ```

- venv 해제

    ```bash
    deactivate
    ```

- requirements.txt에 설치한 패키지 저장

    ```bash
    pip freeze > requirements.txt     
    ```

- requirements.txt의 패키지 설치하기

    ```bash
    pip install -r requirements.txt
    ```

## windows를 위한 설정

```python
# ============
# Windows 전용 설정
# ============
"""python
if root is not None:
    windows일 때 실행할 코드
"""

import tkinter as tk

root: tk.Tk | None = None
is_windows = platform.system() == "Windows"
if is_windows:
    root = tk.Tk()
    root.title(f"Pi Game ({WIDTH}x{HEIGHT})")
    label = tk.Label(root)
    label.pack()
```

## 기본 세팅

## main.py

`if __name__ == "__main__":`

```python
if __name__ == "__main__":
    main_loop()
    if root is not None:
        root.mainloop()

```

### objects

화면에 그릴 것들을 만든다.
list로 만들어서 관리한다.

```python
# ============
# objects
# ============
import mushitroom_object

objects: list[mushitroom_object.MushitroomObject] = []
shit_1 = mushitroom_object.MushitroomObject(1, 2, 413, "black")
objects.append(shit_1)
```

### 키보드 이벤트

키보드 이벤트는 windows 환경에서 테스트 하기 위해 작성함.
raspberry pi zero2에서 쓰려면 gpio 인터럽트 등으로 대체

```python
# ====
# 키보드 이벤트 (Windows에서 Test 하기 위함)
# ====

pressed_keys = set()


def on_key_press(event):
    # 키보드를 누르면 set에 추가 (예: 'w', 'Up', 'space')
    pressed_keys.add(event.keysym)


def on_key_release(event):
    # 키보드를 떼면 set에서 제거
    if event.keysym in pressed_keys:
        pressed_keys.remove(event.keysym)


def keyboard_event():
    if "Up" in pressed_keys or "w" in pressed_keys:
        print("위")
    if "Down" in pressed_keys or "s" in pressed_keys:
        print("아래")
    if "Left" in pressed_keys or "a" in pressed_keys:
        print("좌")
    if "Right" in pressed_keys or "d" in pressed_keys:
        print("우")


# keyboard event 바인드
if root is not None:
    root.bind("<KeyPress>", on_key_press)
    root.bind("<KeyRelease>", on_key_release)

```

## mushitroom_config.py

```python


# ============
# 설정파일 불러오기
# ============
import mushitroom_config
WIDTH: int = mushitroom_config.DISPLAY_WIDTH
HEIGHT: int = mushitroom_config.DISPLAY_HEIGHT
BG_COLOR = mushitroom_config.BG_COLOR
FPS = int(1000 / mushitroom_config.FPS)

```

## SQLite 데이터베이스

### 1. 개요

**SQLite**는 별도의 서버 프로세스(MySQL, PostgreSQL 등) 설치가 필요 없는 **경량화된 파일 기반의 관계형 데이터베이스(RDBMS)**

- **Zero Configuration:** 설정이나 관리자가 필요 없음.
- **Single File:** 데이터베이스 전체가 디스크 위의 파일 하나(예: `data.db`)에 저장되므로 이동과 백업이 간편.
- **Standard:** 라즈베리파이와 같은 임베디드 시스템, 모바일 앱, 데스크톱 소프트웨어의 로컬 저장소로 널리 사용됨.

### 2. 파이썬에서 사용법

파이썬은 `sqlite3` 모듈을 기본 내장하고 있어 별도의 설치 없이 바로 사용할 수 있음.

**기본 사용 패턴:**

  1. **연결 (Connect):** DB 파일과 연결.
  2. **커서 (Cursor):** SQL 명령을 실행할 객체를 생성.
  3. **실행 (Execute):** SQL 문법으로 데이터를 조작.
  4. **커밋 (Commit):** 변경된 내용을 파일에 확정 저장.

```python
import sqlite3

# 1. DB 파일 연결 (없으면 자동 생성)
conn = sqlite3.connect("mushitroom.db")
cursor = conn.cursor()

# 2. 테이블 생성 (IF NOT EXISTS로 중복 방지)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER
    )
""")

# 3. 데이터 삽입 (보안을 위해 ? 플레이스홀더 사용 권장)
cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", ("Mushitroom", 100))
conn.commit()  # ★ 중요: 커밋을 해야 저장이 완료됨

# 4. 데이터 조회
cursor.execute("SELECT * FROM scores ORDER BY score DESC")
print(cursor.fetchall())

# 5. 연결 종료
conn.close()
```

```mermaid
erDiagram
    mushitroom_user ||--|| mushitroom_state : "has (1:1)"
    mushitroom_user ||--o{ scores : "records (1:N)"
    
    mushitroom_user {
        text id PK "UUID"
        text username "User Nickname"
        timestamp updated "Last Active"
    }

    mushitroom_state {
        text id PK "State UUID"
        text user_id FK "Link to User"
        int money "Currency"
        timestamp updated "Last Save"
    }

    scores {
        int id PK "Auto Increment"
        text user_id FK "Link to User"
        int score "Game Score"
        timestamp reg_date "Record Time"
    }
