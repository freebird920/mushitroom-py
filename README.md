# MUSHITROOM

- [MUSHITROOM](#mushitroom)
  - [python 설정](#python-설정)
    - [python .venv 설정](#python-venv-설정)
  - [windows를 위한 설정](#windows를-위한-설정)
  - [기본 세팅](#기본-세팅)
  - [main.py](#mainpy)
    - [objects](#objects)
    - [키보드 이벤트](#키보드-이벤트)
  - [mushitroom\_config.py](#mushitroom_configpy)

## python 설정

### python .venv 설정

- venv 초기화

    ```bash
    python -m venv .venv
    ```

- venv 활성화

    ```bash
    .venv\Scripts\activate
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
