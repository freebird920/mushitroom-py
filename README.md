# MUSHITROOM

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

### 키보드 이벤트

## mushitroom_config.py
