import os
import platform
import subprocess
from enum import Enum

# [수정 1] 상단 import winsound 제거 (함수 안으로 이동)


class AudioList(Enum):
    CLICK = "src/assets/audio/click_001.wav"
    BGM_01 = "src/assets/audio/bgm_01.wav"


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

    def play_sound(self, audio: AudioList, loop: bool = False):
        """
        소리 재생 함수
        loop=True일 경우 무한 반복 (BGM용)
        """
        if not os.path.exists(audio.value):
            print(f"❌ 파일 없음: {audio.value}")
            return

        try:
            if self._system_os == "Windows":
                import winsound

                flags = winsound.SND_FILENAME | winsound.SND_ASYNC
                if loop:
                    flags |= winsound.SND_LOOP

                winsound.PlaySound(audio.value, flags)

            elif self._system_os == "Linux":
                # 기존에 반복 재생 중인 BGM이 있다면 끄고 시작
                # self.stop_sound()

                if loop:
                    # [수정] 윈도우 Pylance 에러 방지: os.setsid 안전하게 호출
                    setsid_func = getattr(os, "setsid", None)

                    cmd = f"while true; do aplay -q {audio.value}; done"

                    # 리눅스에서만 setsid_func가 존재하므로 실행됨
                    self._bgm_process = subprocess.Popen(
                        cmd, shell=True, preexec_fn=setsid_func
                    )
                else:
                    subprocess.Popen(["aplay", "-q", audio.value])

        except Exception as e:
            print(f"⚠️ 사운드 재생 오류: {e}")
