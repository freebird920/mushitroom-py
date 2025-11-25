import zipapp
import os
import shutil
import tempfile
from pathlib import Path


def build():
    # 1. 최종 결과물 위치 설정
    os.makedirs("dist", exist_ok=True)
    final_output_path = Path("dist") / "mushitroom.pyz"
    source_dir = Path(".")

    print(f"🔨 빌드 시작: {source_dir.resolve()}")

    # 2. 필터 함수 (불필요한 파일 제외)
    def filter_func(path: Path):
        ignore_list = {
            ".venv",
            "dist",
            ".git",
            ".vscode",
            "__pycache__",
            "build.py",
            "mushitroom.pyz",
            ".idea",
        }
        for part in path.parts:
            if part in ignore_list:
                return False
        return True

    # 3. [핵심] 임시 폴더에서 빌드 후 이동 (에러 방지)
    # 시스템의 임시 폴더(Temp)는 프로젝트 폴더 바깥에 있으므로 안전함
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output_path = Path(temp_dir) / "mushitroom.pyz"

        try:
            zipapp.create_archive(
                source=source_dir,
                target=temp_output_path,
                interpreter="/usr/bin/env python3",
                main="main:main",
                filter=filter_func,
                compressed=True,
            )

            # 4. 임시 폴더 -> 진짜 dist 폴더로 이동
            if final_output_path.exists():
                os.remove(final_output_path)  # 기존 파일 있으면 삭제

            shutil.move(str(temp_output_path), str(final_output_path))

            print(f"✅ 빌드 성공! 파일 위치: {final_output_path.absolute()}")

        except Exception as e:
            print(f"❌ 빌드 실패: {e}")


if __name__ == "__main__":
    build()
