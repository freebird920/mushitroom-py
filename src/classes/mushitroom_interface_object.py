import src.classes.mushitroom_object as mushitroom_object
import os
import io
import zipfile
import PIL.ImageFont
from typing import List, Callable
import posixpath
from PIL.ImageDraw import ImageDraw


# import mushitroom_enums
from src.settings.mushitroom_enums import FontWeight
from src.settings.mushitroom_enums import ObjectType


def noneFunction():
    pass


class MushitroomInterfaceObject(mushitroom_object.MushitroomObject):
    text: str | None = ""
    text_color: str = "black"
    is_selected = False
    on_action: Callable = noneFunction

    def __init__(
        self,
        index: int,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        text: str | None = None,
        text_color: str = "black",
        font_size: int = 15,
        font_weight: FontWeight = FontWeight.REGULAR,
        id: str | None = None,
        on_action: Callable = noneFunction,  # [추가] 엔터 눌렀을 때 실행할 함수
    ):
        super().__init__(
            x, y, width, height, color, id, object_type=ObjectType.INTERFACE
        )

        # 1. 일단 운영체제 기준 경로를 만듭니다.
        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(
            current_dir, "../", "assets", "fonts", font_weight.value
        )

        try:
            # [CASE 1] 개발 환경 (일반 폴더)
            # OS가 ../ 처리를 알아서 해주므로 그냥 읽힙니다.
            self.font = PIL.ImageFont.truetype(font_path, font_size)

        except (OSError, FileNotFoundError):
            # [CASE 2] .pyz 배포 환경
            # 폰트 로드에 실패하면 Zip 내부라고 가정하고 로직을 실행합니다.
            try:
                # 경로 구분자를 무조건 / 로 통일 (Zip은 /만 씁니다)
                unified_path = font_path.replace("\\", "/")

                if ".pyz/" in unified_path:
                    # 1. Zip 파일 경로와 내부 경로 쪼개기
                    zip_file_path, internal_path_raw = unified_path.split(".pyz/")
                    zip_file_path += ".pyz"

                    # 2. [핵심 수정] 내부 경로의 ".." 계산하기
                    # 예: "src/classes/../assets/font.ttf" -> "src/assets/font.ttf"로 변환
                    internal_path_clean = posixpath.normpath(internal_path_raw)

                    # 3. Zip 열고 데이터 읽기
                    with zipfile.ZipFile(zip_file_path, "r") as z:
                        # Zip 안에서 파일 찾기 (깨끗해진 경로 사용)
                        font_data = z.read(internal_path_clean)

                        # 바이트 데이터를 Pillow 폰트로 변환
                        self.font = PIL.ImageFont.truetype(
                            io.BytesIO(font_data), font_size
                        )
                else:
                    # .pyz 파일이 아닌데도 못 찾은 경우 (진짜 경로 에러)
                    print(f"❌ 폰트 경로를 찾을 수 없음: {font_path}")
                    self.font = PIL.ImageFont.load_default()

            except Exception as e:
                unified_path = font_path.replace("\\", "/")
                zip_file_path, internal_path_raw = unified_path.split(".pyz/")
                internal_path_clean = posixpath.normpath(internal_path_raw)
                print(f"❌ 폰트 로드 최종 실패 (기본 폰트 사용): {e}")
                print(
                    f"   - 시도한 내부 경로: {internal_path_clean if 'internal_path_clean' in locals() else '알수없음'}"
                )
                self.font = PIL.ImageFont.load_default()
        self.text = text
        self.text_color = text_color
        self.index = index
        self.on_action = on_action

    def select(self):
        self.is_selected = True

    # 선택 상태 끄기 (다른 놈으로 넘어갈 때 필요)
    def deselect(self):
        self.is_selected = False

    # [추가] 액션 실행 (딸깍!)
    def trigger_action(self):
        if self.on_action:
            print(f"[{self.text}] 버튼 실행!")
            self.on_action()  # 저장된 함수 실행

    def draw(self, canvas: ImageDraw):
        super().draw(canvas)
        color_override = self.text_color
        if self.is_selected:
            color_override = "red"
        if self.text is not None:
            canvas.text(
                (self.x, self.y),
                self.text,
                font=self.font,
                fill=color_override,
                anchor="mm",  # 가운데 정렬
            )


class MushitroomInterfaceGroup:
    def __init__(self):
        self.elements: List[MushitroomInterfaceObject] = []
        self.current_index: int = 0

    def add_element(self, element: MushitroomInterfaceObject):
        """UI 요소를 그룹에 추가합니다."""
        self.elements.append(element)

        if len(self.elements) == 1:
            self.current_index = 0
            element.select()

    def select_next(self):
        """다음 메뉴로 이동 (마지막이면 처음으로)"""
        if not self.elements:
            return  # 리스트 비었으면 패스

        # 1. 지금 선택된 놈 불 끄기
        self.elements[self.current_index].deselect()

        # 2. 번호 증가 (나머지 연산 % 으로 순환)
        self.current_index = (self.current_index + 1) % len(self.elements)

        # 3. 새로 선택된 놈 불 켜기
        self.elements[self.current_index].select()
        print(f"이동함 -> {self.current_index}번")

    def select_prev(self):
        """이전 메뉴로 이동"""
        if not self.elements:
            return

        self.elements[self.current_index].deselect()

        # 번호 감소 (음수 되면 알아서 뒤로 감)
        self.current_index = (self.current_index - 1) % len(self.elements)

        self.elements[self.current_index].select()
        print(f"이동함 -> {self.current_index}번")

    def execute_current(self):
        """지금 선택된 놈의 액션(딸깍) 실행"""
        if self.elements:
            target = self.elements[self.current_index]
            print(f"실행 -> {target.text}")
            target.trigger_action()

    def draw(self, canvas: ImageDraw):
        """그룹 안에 있는 모든 UI를 한방에 그리기"""
        for element in self.elements:
            element.draw(canvas)
