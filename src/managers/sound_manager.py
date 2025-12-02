import os
import platform
import subprocess
from enum import Enum

# [수정 1] 상단 import winsound 제거 (함수 안으로 이동)


class AudioList(Enum):
    CLICK = "src/assets/audio/click_001.wav"
    BGM_01 = "src/assets/audio/bgm_01"


class SoundManager:
    _instance: "SoundManager | None" = None
    _system_os: str

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._system_os = platform.system()
            self.initialized = True

    def play_sound(self, audio: AudioList):
        if not os.path.exists(audio.value):
            print(f"❌ 파일 없음: {audio.value}")
            return

        try:
            if self._system_os == "Windows":
                # [수정 2] 사용하는 시점에 import (Pylance 경고 해결)
                import winsound

                winsound.PlaySound(
                    audio.value, winsound.SND_FILENAME | winsound.SND_ASYNC
                )

            elif self._system_os == "Linux":
                subprocess.Popen(["aplay", "-q", audio.value])

        except Exception as e:
            print(f"⚠️ 사운드 재생 오류: {e}")
