import os
import io
import zipfile
import posixpath
from PIL import Image, ImageFont, UnidentifiedImageError

# --------------------------------------------------------------------------
# [Global Cache Storage]
# 이미지는 (경로, 너비, 높이)를 키로 저장
# 폰트는 (경로, 크기)를 키로 저장
# --------------------------------------------------------------------------
_IMAGE_CACHE: dict[tuple[str, int, int], Image.Image] = {}
_FONT_CACHE: dict[tuple[str, int], ImageFont.ImageFont | ImageFont.FreeTypeFont] = {}


def clear_caches():
    """
    [메모리 관리] 캐시된 모든 이미지와 폰트를 메모리에서 해제합니다.
    씬(Scene) 전환 시나 메모리 부족 시 호출하세요.
    """
    _IMAGE_CACHE.clear()
    _FONT_CACHE.clear()


def _get_resource_stream(path: str) -> io.BytesIO | None:
    """
    [내부 함수] 경로를 받아 파일 데이터를 바이트 스트림(io.BytesIO)으로 반환합니다.
    (IO 작업이므로 캐싱하지 않고, 호출 시마다 스트림을 새로 엽니다.)
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

            # 내부 경로 정규화
            internal_path_clean = posixpath.normpath(internal_path_raw)

            # Zip 열고 데이터 읽기
            with zipfile.ZipFile(zip_file_path, "r") as z:
                file_data = z.read(internal_path_clean)
                return io.BytesIO(file_data)
        except KeyError:
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
    폰트를 로드합니다. (캐싱 적용됨)
    동일한 경로와 크기의 요청이 들어오면 메모리에서 반환합니다.
    """
    # 1. 캐시 확인
    cache_key = (path, size)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    # 2. 리소스 로드 (캐시에 없을 경우)
    font_stream = _get_resource_stream(path)

    if font_stream:
        try:
            font = ImageFont.truetype(font_stream, size)
            # 3. 캐시에 저장
            _FONT_CACHE[cache_key] = font
            return font
        except Exception as e:
            print(f"❌ 폰트 생성 실패: {path} / {e}")

    # 실패 시 기본 폰트 (기본 폰트는 캐싱하지 않음)
    return ImageFont.load_default()


def load_resized_image(path: str, width: int, height: int) -> Image.Image | None:
    """
    이미지를 로드하고 리사이징하여 반환합니다. (캐싱 적용됨)
    동일한 경로, 너비, 높이의 요청은 메모리에서 즉시 반환합니다.
    """
    # 1. 캐시 확인
    cache_key = (path, width, height)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    # 2. 리소스 로드
    img_stream = _get_resource_stream(path)

    if img_stream:
        try:
            with Image.open(img_stream) as img:
                img = img.convert("RGBA")
                # NEAREST는 도트 게임에 필수
                resized_img = img.resize(
                    (width, height), resample=Image.Resampling.NEAREST
                )

                # 3. 캐시에 저장
                _IMAGE_CACHE[cache_key] = resized_img
                return resized_img
        except UnidentifiedImageError:
            print(f"❌ 이미지 식별 불가: {path}")
        except Exception as e:
            print(f"❌ 이미지 처리 실패: {path} / {e}")

    return None
