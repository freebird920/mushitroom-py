import os
import io
import zipfile
import posixpath
from PIL import Image, ImageFont, UnidentifiedImageError


def _get_resource_stream(path: str) -> io.BytesIO | None:
    """
    [내부 함수] 경로를 받아 파일 데이터를 바이트 스트림(io.BytesIO)으로 반환합니다.
    1. 일반 파일 시스템을 먼저 찾습니다.
    2. 없으면 .pyz (Zip) 내부 경로를 찾습니다.
    """
    # 1. 경로 구분자 통일
    unified_path = path.replace("\\", "/")

    # [CASE 1] 일반 파일 시스템에 존재하는 경우
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return io.BytesIO(f.read())
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {path} / {e}")
            return None

    # [CASE 2] .pyz (Zip) 내부에 존재하는 경우
    if ".pyz/" in unified_path:
        try:
            zip_file_path, internal_path_raw = unified_path.split(".pyz/")
            zip_file_path += ".pyz"

            # 내부 경로 정규화 (../ 등을 처리해서 절대 경로처럼 만듦)
            internal_path_clean = posixpath.normpath(internal_path_raw)

            # Zip 열고 데이터 읽기
            with zipfile.ZipFile(zip_file_path, "r") as z:
                file_data = z.read(internal_path_clean)
                return io.BytesIO(file_data)
        except KeyError:
            # Zip 안에 해당 파일이 없을 때
            pass
        except Exception as e:
            print(f"❌ Zip 내부 읽기 실패: {path} / {e}")

    # 못 찾음
    print(f"⚠️ 리소스를 찾을 수 없음: {path}")
    return None


def load_custom_font(
    path: str, size: int
) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """
    폰트를 로드합니다. 실패 시 기본 폰트를 반환합니다.
    """
    # 공통 로직을 통해 데이터 스트림 가져오기
    font_stream = _get_resource_stream(path)

    if font_stream:
        try:
            return ImageFont.truetype(font_stream, size)
        except Exception as e:
            print(f"❌ 폰트 생성 실패: {path} / {e}")

    # 실패 시 기본 폰트
    return ImageFont.load_default()


def load_resized_image(path: str, width: int, height: int) -> Image.Image | None:
    """
    이미지를 로드하고 RGBA 변환 및 리사이징하여 반환합니다.
    """
    # 공통 로직을 통해 데이터 스트림 가져오기
    img_stream = _get_resource_stream(path)

    if img_stream:
        try:
            with Image.open(img_stream) as img:
                img = img.convert("RGBA")
                return img.resize((width, height))
        except UnidentifiedImageError:
            print(f"❌ 이미지 식별 불가: {path}")
        except Exception as e:
            print(f"❌ 이미지 처리 실패: {path} / {e}")

    return None
