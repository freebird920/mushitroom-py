import random


class NameGenerator:
    """
    게임 컨셉에 맞는 랜덤 닉네임을 생성하는 클래스
    """

    # 관형사/형용사 리스트
    ADJECTIVES = [
        "축축한",
        "메마른",
        "화려한",
        "수줍은",
        "독이든",
        "배고픈",
        "춤추는",
        "노래하는",
        "수상한",
        "맛있는",
        "거대한",
        "조그만",
        "미친",
        "우울한",
        "행복한",
        "비에젖은",
        "바삭한",
        "쫄깃한",
        "맹독성",
        "환각의",
        "빨간",
        "파란",
        "보라색",
        "황금",
        "무지개",
        "건방진",
        "게으른",
        "부지런한",
        "잠오는",
        "윤어게인",
    ]

    # 명사 리스트
    NOUNS = [
        "버섯",
        "송이",
        "포자",
        "균사",
        "곰팡이",
        "트러플",
        "표고",
        "양송이",
        "느타리",
        "팽이",
        "광대버섯",
        "영지버섯",
        "상황버섯",
        "동충하초",
    ]

    @classmethod
    def get_random_name(cls) -> str:
        """
        랜덤한 닉네임을 생성하여 반환합니다.
        예: '축축한 곰팡이', '춤추는 독버섯'
        """
        adj = random.choice(cls.ADJECTIVES)
        noun = random.choice(cls.NOUNS)

        # 10% 확률로 뒤에 숫자를 붙여서 유니크함 더하기 (선택사항)
        if random.random() < 0.1:
            number = random.randint(1, 99)
            return f"{adj} {noun} {number}호"

        return f"{adj} {noun}"
