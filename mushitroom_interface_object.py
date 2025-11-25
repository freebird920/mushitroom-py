from PIL.ImageDraw import ImageDraw
import mushitroom_object
from mushitroom_enums import FontWeight
from mushitroom_enums import ObjectType
import os
import PIL.ImageFont

from typing import List
from PIL import ImageDraw

# from mushitroom_interface_object import MushitroomInterfaceObject


class MushitroomInterfaceObject(mushitroom_object.MushitroomObject):
    text: str | None = ""
    text_color: str = "black"
    is_selected = False

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
        on_action=None,  # [추가] 엔터 눌렀을 때 실행할 함수
    ):
        super().__init__(
            x, y, width, height, color, id, object_type=ObjectType.INTERFACE
        )

        current_dir = os.path.dirname(__file__)
        font_path = os.path.join(current_dir, "assets", "fonts", font_weight.value)

        self.font = PIL.ImageFont.truetype(font_path, font_size)
        self.text = text
        self.text_color = text_color
        self.index = index
        self.on_action = on_action  # 함수 저장

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

    def draw(self, canvas: ImageDraw.ImageDraw):
        super().draw(canvas)
        if self.text is not None:
            canvas.text(
                (self.x, self.y),
                self.text,
                font=self.font,
                fill=self.text_color,
                anchor="mm",  # 가운데 정렬
            )


class MushitroomInterfaceGroup:
    def __init__(self):
        # UI 요소들을 담을 리스트
        self.elements: List[MushitroomInterfaceObject] = []
        # 현재 선택된 놈의 번호 (0번부터 시작)
        self.current_index: int = 0

    def add_element(self, element: MushitroomInterfaceObject):
        """UI 요소를 그룹에 추가합니다."""
        self.elements.append(element)

        # 만약 이게 첫 번째로 추가된 놈이라면? -> 바로 선택 상태로 만듦 (초기화)
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

    def draw(self, canvas: ImageDraw.ImageDraw):
        """그룹 안에 있는 모든 UI를 한방에 그리기"""
        for element in self.elements:
            element.draw(canvas)
